from django.urls import path, include
from rest_framework.routers import DefaultRouter
from HLS_viewer_backend.views import (
    DocumentTemplateViewSet,
    GeneratedDocumentViewSet,
    api_overview
)

router = DefaultRouter()
router.register(r'templates', DocumentTemplateViewSet, basename='document-templates')
router.register(r'documents', GeneratedDocumentViewSet, basename='generated-documents')

urlpatterns = [
    path('', api_overview, name='api-overview'),
    path('', include(router.urls)),
]