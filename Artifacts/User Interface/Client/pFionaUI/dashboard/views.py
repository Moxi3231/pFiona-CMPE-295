
from django.http import HttpResponse
from django.shortcuts import render

def dashboard(request):
    return render(request, 'dashboard/dashboard.html')

def logs(request):
    return render(request, 'dashboard/logs.html')

def data(request):
    return render(request, 'dashboard/data.html')

def graphs(request):
    return render(request, 'dashboard/graphs.html')

def control(request):
    return render(request, 'dashboard/control.html')