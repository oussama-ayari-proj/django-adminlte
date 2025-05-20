from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def index(request):
    return render(request, 'plannifications/index.html')

def index_sans_contraintes(request):
    return render(request, 'plannifications/index_sans_contraintes.html')