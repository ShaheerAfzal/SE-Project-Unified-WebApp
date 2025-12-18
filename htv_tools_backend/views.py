from django.shortcuts import render
from django.views.generic import TemplateView
from .models import HTVConfiguration
from .serializers import HTVConfigurationSerializer
from rest_framework import viewsets

# Create your views here.

class HTVConfigView(TemplateView):
    """Renders the HTV Config tool using a Class-Based View."""
    template_name = 'htv_tools/htv-config-index.html'

class HTVProgrammerView(TemplateView):
    """Renders the HTV Programmer tool using a Class-Based View."""
    template_name = 'htv_tools/htv-programmer-index.html'

# This handles the API logic for saving/retrieving data
class HTVConfigurationViewSet(viewsets.ModelViewSet):
    queryset = HTVConfiguration.objects.all()
    serializer_class = HTVConfigurationSerializer
    lookup_field = 'imei' # Allow lookups by IMEI instead of just ID