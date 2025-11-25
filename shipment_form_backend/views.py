# views.py
from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from django.http import HttpResponse
from django.template.response import TemplateResponse

from .models import DocumentTemplate, GeneratedDocument
from .serializers import DocumentTemplateSerializer, GeneratedDocumentSerializer


# -------------------------------------------
# API OVERVIEW
# -------------------------------------------
@api_view(['GET'])
def api_overview(request):
    return Response({
        "templates CRUD": "/templates/",
        "templates render view": "/templates/<id>/render/",
        "documents CRUD": "/documents/",
        "documents preview": "/documents/<id>/preview/",
    })


# -------------------------------------------
# DOCUMENT TEMPLATES VIEWSET (CRUD)
# -------------------------------------------
class DocumentTemplateViewSet(viewsets.ModelViewSet):
    queryset = DocumentTemplate.objects.all().order_by("-created_at")
    serializer_class = DocumentTemplateSerializer

    # Extract fields on create
    def perform_create(self, serializer):
        instance = serializer.save()
        instance.extract_and_populate_fields()

    # Extract fields if new file uploaded
    def perform_update(self, serializer):
        old_file = self.get_object().file
        instance = serializer.save()

        if old_file != instance.file:
            instance.extract_and_populate_fields()

    # ---------------------------------------------------
    # RENDER TEMPLATE (simple HTML render for inspection)
    # ---------------------------------------------------
    @action(detail=True, methods=['GET'])
    def render(self, request, pk=None):
        template = self.get_object()

        context = {
            "template_name": template.name,
            "fields": template.fields,
        }

        # Renders templates/template_render.html
        return TemplateResponse(request, "template_render.html", context)


# -------------------------------------------
# GENERATED DOCUMENTS VIEWSET (CRUD)
# -------------------------------------------
class GeneratedDocumentViewSet(viewsets.ModelViewSet):
    queryset = GeneratedDocument.objects.all().order_by("-created_at")
    serializer_class = GeneratedDocumentSerializer

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        generated_doc = serializer.save(created_by=user)

        # Automatically fill key_field_value
        template = generated_doc.template
        if template.key_field:
            generated_doc.key_field_value = generated_doc.field_values.get(template.key_field)
            generated_doc.save()

    # ---------------------------------------------------
    # PREVIEW GENERATED DOCUMENT (download .docx)
    # ---------------------------------------------------
    @action(detail=True, methods=['GET'])
    def preview(self, request, pk=None):
        document = self.get_object()
        output = document.generate_and_attach_file()

        filename = f"{document.template.name}-{document.key_field_value or 'preview'}.docx"

        response = HttpResponse(
            output.read(),
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        response["Content-Disposition"] = f'attachment; filename=\"{filename}\"'

        return response
