# views.py
from django.forms import ValidationError
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse, FileResponse
from django.shortcuts import get_object_or_404, render

from .models import DocumentTemplate, GeneratedDocument
from .serializers import *




def shipment_index(request):
    return render(request, "shipment_form/index.html")


class DocumentTemplateViewSet(viewsets.ModelViewSet):
    queryset = DocumentTemplate.objects.all().order_by("-created_at")

    def get_serializer_class(self):
        # 1. CREATE: Requires File (Upload Serializer)
        if self.action == "create":
            return DocumentTemplateUploadSerializer

        # 2. UPDATE: File is Optional (Update Serializer)
        if self.action in ["update", "partial_update"]:
            return DocumentTemplateUpdateSerializer  # <--- CHANGED THIS

        # 3. LIST/RETRIEVE: Read-only (Standard Serializer)
        return DocumentTemplateSerializer          # for listing/get

    # --- CREATE --- (replaced with save logic in GeneratedDocument model)
    # def perform_create(self, serializer):
    #     if "file" not in serializer.validated_data:
    #         raise ValidationError("A .docx file is required when creating a template.")

    #     instance = serializer.save()
    #     instance.extract_and_populate_fields()

    # --- UPDATE ---
    def perform_update(self, serializer):
        instance_before = self.get_object()
        old_file = instance_before.file

        instance = serializer.save()

        # Re-extract fields ONLY if the file changed
        if old_file != instance.file and instance.file:
            instance.extract_and_populate_fields()

    # --- DELETE ---
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # This deletes the record from DB. 
        # Because of on_delete=models.CASCADE in the other model, 
        # it will also delete all associated GeneratedDocuments.
        instance.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    # GET /templates/<id>/fields/
    @action(detail=True, methods=['get'])
    def fields(self, request, pk=None):
        template = self.get_object()
        return Response({
            "fields": template.fields,
            "key_field": template.key_field
        })

    # POST /templates/<id>/generate/
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

    # GET /templates/<id>/documents/
    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        """
        Returns a list of GeneratedDocuments for this specific template.
        Endpoint: GET /templates/<id>/documents/
        """
        template = self.get_object()
        # We use the related_name="documents" from your model
        docs = template.documents.all().order_by("-created_at")
        
        serializer = GeneratedDocumentSerializer(docs, many=True)
        return Response(serializer.data)





class GeneratedDocumentViewSet(viewsets.ModelViewSet):
    queryset = GeneratedDocument.objects.all().order_by("-created_at")
    serializer_class = GeneratedDocumentSerializer

    def perform_create(self, serializer):
        # We only need to handle user assignment here now
        # The key_field logic is handled in the Model.save()!
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(created_by=user)

    # GET /documents/<id>/preview/
    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        doc_gen = self.get_object()
        
        # Generate file in memory
        file_stream = doc_gen.generate_and_attach_file()
        doc_gen.key_field_value
        # Create filename
        filename = f"{doc_gen.template.name}-{doc_gen.key_field_value or 'generated'}.docx"
        
        # Use FileResponse for better file handling
        return FileResponse(
            file_stream, 
            as_attachment=True, 
            filename=filename
        )
