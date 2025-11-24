# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'templates', views.DocumentTemplateViewSet, basename='template')
router.register(r'documents', views.GeneratedDocumentViewSet, basename='document')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/overview/', views.api_overview, name='api-overview'),
]