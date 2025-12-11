# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from shipment_form_backend.views import (
    DocumentTemplateViewSet,
    GeneratedDocumentViewSet,
    shipment_index,
)

router = DefaultRouter()
router.register(r'templates', DocumentTemplateViewSet, basename='document-templates')
router.register(r'documents', GeneratedDocumentViewSet, basename='generated-documents')

urlpatterns = [
    path('', include(router.urls)),
    path("shipment/", shipment_index, name="shipment_home"),
]
