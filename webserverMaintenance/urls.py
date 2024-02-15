from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_page, name='restartproxy_main_page'),
    path('execute-remote-command/<str:server_name>/<str:command_name>/', views.execute_remote_command_by_server_and_command_name, name='execute_remote_command_by_server_and_command_name'),
    # Add other paths for other remote commands
]
