from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.serial_view, name='serial'),
]