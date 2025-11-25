# views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from .models import DocumentTemplate, GeneratedDocument
from .serializers import DocumentTemplateSerializer, DocumentTemplateUploadSerializer, GeneratedDocumentSerializer




def shipment_index(request):
    return render(request, "shipment_form/index.html")


class DocumentTemplateViewSet(viewsets.ModelViewSet):
    queryset = DocumentTemplate.objects.all().order_by("-created_at")
    serializer_class = DocumentTemplateSerializer

    # CREATE — extract fields immediately
    def perform_create(self, serializer):
        instance = serializer.save()
        instance.extract_and_populate_fields()

    # UPDATE — if a file changed, re-extract fields
    def perform_update(self, serializer):
        old_file = self.get_object().file
        instance = serializer.save()

        if old_file != instance.file:
            instance.extract_and_populate_fields()

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
        data["template"] = str(template.id)

        ser = DocumentGenerationSerializer(data=data)
        if ser.is_valid():
            doc = ser.save()

            # Auto-set key_field_value
            if template.key_field:
                doc.key_field_value = doc.field_values.get(template.key_field)
                doc.save()

            return Response(GeneratedDocumentSerializer(doc).data, status=201)

        return Response(ser.errors, status=400)

    # GET /templates/<id>/documents/
    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        template = self.get_object()
        docs = template.documents.all().order_by("-created_at")
        return Response(GeneratedDocumentSerializer(docs, many=True).data)



class GeneratedDocumentViewSet(viewsets.ModelViewSet):
    queryset = GeneratedDocument.objects.all().order_by("-created_at")
    serializer_class = GeneratedDocumentSerializer

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        doc = serializer.save(created_by=user)

        template = doc.template
        if template.key_field:
            doc.key_field_value = doc.field_values.get(template.key_field)
            doc.save()

    # GET /documents/<id>/preview/
    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        doc = self.get_object()
        output = doc.generate_and_attach_file()

        filename = f"{doc.template.name}-{doc.key_field_value or 'generated'}.docx"

        response = HttpResponse(
            output.read(),
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        return response
