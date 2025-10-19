from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets
from .models import Stream
from .serializers import StreamSerializer

class StreamViewSet(viewsets.ModelViewSet):
    queryset = Stream.objects.all().order_by('-created_at')
    serializer_class = StreamSerializer
