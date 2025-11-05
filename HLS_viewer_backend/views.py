from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import *
from rest_framework import viewsets
from .serializers import *

# Create your views here.
class StreamViewSet(viewsets.ModelViewSet):
    queryset = Stream.objects.all().order_by('-created_at')
    serializer_class = StreamSerializer


class HlsIndexView(View):
    template_name = 'hls-viewer/index.html'

    def get(self, request):
        streams = Stream.objects.filter(is_active=True)
        return render(request, self.template_name, {'streams': streams})


class GateCameraView(View):
    template_name = 'hls-viewer/gate-camera.html'

    def get(self, request, stream_id=None):
        stream = get_object_or_404(Stream, id=stream_id) if stream_id else None
        return render(request, self.template_name, {'stream': stream})