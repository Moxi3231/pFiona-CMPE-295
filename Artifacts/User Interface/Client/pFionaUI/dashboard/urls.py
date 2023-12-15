from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('logs/', views.logs, name='logs'),
    path('data/', views.data, name='data'),
    path('graphs/', views.graphs, name='graphs'),
    path('control/', views.control, name='control')
]
