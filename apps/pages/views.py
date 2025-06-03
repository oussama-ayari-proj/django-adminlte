from django.shortcuts import render
from .models import UF

# Create your views here.

def index(request):
    ufs = UF.objects.all()
    return render(request, 'pages/index.html', {'records': ufs})
