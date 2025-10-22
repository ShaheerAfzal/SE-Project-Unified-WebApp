from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'streams', StreamViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('viewer/', HlsIndexView.as_view(), name='hls_index'),
    path('viewer/gate/<int:stream_id>/', GateCameraView.as_view(), name='gate_camera'),
]
