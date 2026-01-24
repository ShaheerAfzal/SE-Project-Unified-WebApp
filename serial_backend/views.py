from django.shortcuts import render

# Create your views here.
def serial_view(request):
    return render(request, 'serial/serial-index.html')