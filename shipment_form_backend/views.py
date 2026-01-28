import os
import sys
import subprocess
import tempfile
from django.forms import ValidationError
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse, FileResponse
from django.shortcuts import get_object_or_404, render

from .models import DocumentTemplate, GeneratedDocument
from .serializers import *

# Try importing docx2pdf for Windows Dev environment
try:
    from docx2pdf import convert as windows_convert
    DOCX2PDF_AVAILABLE = True
except ImportError:
    DOCX2PDF_AVAILABLE = False

def shipment_index(request):
    return render(request, "shipment_form/index.html")

def convert_to_pdf_server_friendly(input_path, output_path):
    """
    Hybrid conversion logic:
    1. Windows: Uses docx2pdf (uses MS Word).
    2. Linux/Server: Uses LibreOffice (Headless).
    """
    system_platform = sys.platform

    # --- OPTION A: Windows (Local Dev) ---
    if system_platform == 'win32' and DOCX2PDF_AVAILABLE:
        try:
            windows_convert(input_path, output_path)
            return True, None
        except Exception as e:
            return False, f"Windows Conversion Failed: {str(e)}"

    # --- OPTION B: Linux (Production Server) ---
    # Requires: sudo apt-get install libreoffice
    try:
        # LibreOffice command to convert to PDF
        # --headless: no GUI
        # --outdir: where to save
        output_dir = os.path.dirname(output_path)
        
        # Note: libreoffice saves the file with the same name but .pdf extension
        # We allow it to save, then rename it to our target output_path if needed
        cmd = [
            'libreoffice', '--headless', '--convert-to', 'pdf',
            '--outdir', output_dir,
            input_path
        ]
        
        # Run command
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # LibreOffice naming quirk: It creates 'filename.pdf' in the dir.
        # We need to ensure our output_path matches or rename the result.
        expected_output = input_path.replace('.docx', '.pdf')
        
        if os.path.exists(expected_output) and expected_output != output_path:
            # If we wanted a specific name that is different, rename it
            if os.path.exists(output_path):
                os.remove(output_path)
            os.rename(expected_output, output_path)
            
        return True, None
        
    except FileNotFoundError:
        return False, "LibreOffice not installed. Run: sudo apt-get install libreoffice"
    except subprocess.CalledProcessError as e:
        return False, f"LibreOffice Error: {e.stderr.decode()}"
    except Exception as e:
        return False, f"Server Conversion Failed: {str(e)}"


class DocumentTemplateViewSet(viewsets.ModelViewSet):
    queryset = DocumentTemplate.objects.all().order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "create":
            return DocumentTemplateUploadSerializer
        if self.action in ["update", "partial_update"]:
            return DocumentTemplateUpdateSerializer
        return DocumentTemplateSerializer

    def perform_create(self, serializer):
        if "file" not in serializer.validated_data:
            raise ValidationError("A .docx file is required when creating a template.")
        instance = serializer.save()
        instance.extract_and_populate_fields()

    def perform_update(self, serializer):
        instance_before = self.get_object()
        old_file = instance_before.file
        instance = serializer.save()
        if old_file != instance.file and instance.file:
            instance.extract_and_populate_fields()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=204)

    @action(detail=True, methods=['get'])
    def fields(self, request, pk=None):
        template = self.get_object()
        return Response({
            "fields": template.fields,
            "key_field": template.key_field
        })

    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        template = self.get_object()
        data = request.data.copy()
        data["template"] = template.id
        ser = GeneratedDocumentSerializer(data=data, context={"request": request})
        if ser.is_valid():
            doc = ser.save()
            return Response(GeneratedDocumentSerializer(doc).data, status=201)
        return Response(ser.errors, status=400)

    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        template = self.get_object()
        docs = template.documents.all().order_by("-created_at")
        serializer = GeneratedDocumentSerializer(docs, many=True)
        return Response(serializer.data)


class GeneratedDocumentViewSet(viewsets.ModelViewSet):
    queryset = GeneratedDocument.objects.all().order_by("-created_at")
    serializer_class = GeneratedDocumentSerializer

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(created_by=user)

    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        doc_gen = self.get_object()
        download_format = request.query_params.get('file_format', 'docx')
        
        # 1. Generate DOCX in memory
        docx_stream = doc_gen.generate_and_attach_file()
        
        # 2. Filename setup
        safe_name = "".join([c for c in doc_gen.template.name if c.isalnum() or c in (' ', '-', '_')]).strip()
        
        # Try key_field_value first, then fall back to getting it from field_values
        key_value = doc_gen.key_field_value
        if not key_value and doc_gen.template.key_field:
            key_value = doc_gen.field_values.get(doc_gen.template.key_field)
        
        if key_value:
            safe_key = "".join([c for c in str(key_value) if c.isalnum() or c in (' ', '-', '_')]).strip()
        else:
            safe_key = ''
        filename_base = f"{safe_name}_{safe_key}" if safe_key else f"{safe_name}_generated"

        # 3. PDF Handling
        if download_format == 'pdf':
            # Create a physical temp file (required for external tools)
            with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp_docx:
                tmp_docx.write(docx_stream.getvalue())
                tmp_docx_path = tmp_docx.name
            
            tmp_pdf_path = tmp_docx_path.replace('.docx', '.pdf')
            
            try:
                # CALL THE HELPER FUNCTION
                success, error_msg = convert_to_pdf_server_friendly(tmp_docx_path, tmp_pdf_path)
                
                if not success:
                    return Response({"error": error_msg}, status=500)
                
                # Read PDF back
                with open(tmp_pdf_path, 'rb') as f:
                    pdf_content = f.read()
                    
                response = HttpResponse(pdf_content, content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{filename_base}.pdf"'
                return response
                
            except Exception as e:
                return Response({"error": f"PDF Process Error: {str(e)}"}, status=500)
                
            finally:
                # Clean up temp files
                if os.path.exists(tmp_docx_path):
                    try: os.remove(tmp_docx_path)
                    except: pass
                if os.path.exists(tmp_pdf_path):
                    try: os.remove(tmp_pdf_path)
                    except: pass

        # 4. Default DOCX Handling
        else:
            return FileResponse(
                docx_stream, 
                as_attachment=True, 
                filename=f"{filename_base}.docx"
            )