# views.py
from django.shortcuts import render
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.http import FileResponse, HttpResponse
from .models import DocumentTemplate, GeneratedDocument
from .serializers import (
    DocumentTemplateSerializer,
    DocumentTemplateUploadSerializer,
    GeneratedDocumentSerializer,
    DocumentGenerationSerializer
)

class DocumentTemplateViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = DocumentTemplate.objects.filter(is_active=True)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DocumentTemplateUploadSerializer
        return DocumentTemplateSerializer
    
    def perform_create(self, serializer):
        instance = serializer.save()
        # Auto-extract fields after creation
        instance.extract_and_populate_fields()
    
    def destroy(self, request, *args, **kwargs):
        """Soft delete template by setting is_active to False"""
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['get'])
    def generated_documents(self, request, pk=None):
        """Get all generated documents for this template"""
        template = self.get_object()
        documents = template.generated_documents.all().order_by('-created_at')
        serializer = GeneratedDocumentSerializer(documents, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def generate_document(self, request, pk=None):
        """Generate a document from this template"""
        template = self.get_object()
        
        # Add template_id to request data
        data = request.data.copy()
        data['template_id'] = str(template.id)
        
        serializer = DocumentGenerationSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            generated_doc = serializer.save()
            response_serializer = GeneratedDocumentSerializer(generated_doc)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def preview_fields(self, request, pk=None):
        """Get template fields for frontend form generation"""
        template = self.get_object()
        return Response({
            'id': str(template.id),
            'name': template.name,
            'fields': template.fields,
            'key_field': template.key_field
        })

class GeneratedDocumentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = GeneratedDocumentSerializer
    
    def get_queryset(self):
        """Return documents created by the current user"""
        return GeneratedDocument.objects.filter(created_by=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download generated document"""
        document = self.get_object()
        if document.generated_file:
            response = FileResponse(
                document.generated_file.open(),
                as_attachment=True,
                filename=f"{document.document_name}.docx"
            )
            return response
        return Response(
            {"error": "File not generated yet"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        """Get document data for preview"""
        document = self.get_object()
        return Response(document.get_preview_data())

@api_view(['GET'])
def api_overview(request):
    api_urls = {
        'templates': '/api/templates/',
        'template_detail': '/api/templates/{id}/',
        'template_generated_documents': '/api/templates/{id}/generated_documents/',
        'template_generate_document': '/api/templates/{id}/generate_document/',
        'template_preview_fields': '/api/templates/{id}/preview_fields/',
        'documents': '/api/documents/',
        'document_download': '/api/documents/{id}/download/',
        'document_preview': '/api/documents/{id}/preview/',
    }
    return Response(api_urls)