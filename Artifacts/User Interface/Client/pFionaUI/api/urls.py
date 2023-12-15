from django.urls import path
from . import views

urlpatterns = [
    path('api/graphs/', views.graphs, name='graphs'),
    path('api/add_command/', views.add_command, name='add_command'),
    path('api/add_full_command/', views.add_full_command, name='add_full_command'),
    path('api/next_sample/', views.next_sample, name='next_sample'),
    path('api/free_command_queue', views.free_command_queue, name='free_command_queue'),
    path('api/change_mode/', views.change_mode, name='change_mode'),
    path('api/showdata/', views.showdata, name='showdata'),
    path('api/start_conection/',views.start_conection,name='start_conection'),
    path('api/stop_connection/',views.stop_connection,name='stop_connection'),
    path('api/reset_connection/',views.reset_connection,name='reset_connection'),
    path('api/get_udates/',views.get_udates,name='get_udates'),
    path('api/sample_count_change/',views.sample_count_change,name='sample_count_change'),
    
]
