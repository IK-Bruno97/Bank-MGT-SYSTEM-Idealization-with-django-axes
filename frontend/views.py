from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate

# Create your views here..
def home(request):
        return render(request, 'frontend/frontend.html')
