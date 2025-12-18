from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HTVConfigView, HTVConfigurationViewSet, HTVProgrammerView

app_name = 'htv_tools'
router = DefaultRouter()
router.register(r'config/configs', HTVConfigurationViewSet, basename='htv-configs')
urlpatterns = [
    path('config/', HTVConfigView.as_view(), name='config'),
    path('programmer/', HTVProgrammerView.as_view(), name='programmer'),
    path('', include(router.urls)), # Includes paths like /htv/api/configs/
]