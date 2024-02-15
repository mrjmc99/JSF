# webservermaintenance/views.py
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .models import RemoteServer,RemoteCommand
from webserverMaintenance.utils import execute_remote_command

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SSH_KEY_PATH = os.path.join(BASE_DIR, 'id_rsa')

from django.contrib.auth.decorators import login_required,permission_required
@permission_required('webserverMaintenance.use_webserverMaintenance')
def index(request):
    return render(request, 'oraclequery_main_page.html')





@permission_required('webserverMaintenance.use_webserverMaintenance')
def execute_remote_command_by_server_and_command_name(request, server_name, command_name):
    if request.method == 'POST':
        try:
            server = RemoteServer.objects.get(name=server_name)
            command = RemoteCommand.objects.get(name=command_name)
        except (RemoteServer.DoesNotExist, RemoteCommand.DoesNotExist):
            return HttpResponse("Server or Command not found", status=404)

        result = execute_remote_command(
            server.hostname,
            server.username,
            server.private_key_path,
            command.command,
            request.user
        )

        if result:
            return JsonResponse(result)  # Send JSON response
    return HttpResponse(status=500)


@permission_required('webserverMaintenance.use_webserverMaintenance')
def main_page(request):
    remoteserver = RemoteServer.objects.all()
    return render(request, 'webserverMaintenance_main_page.html', {'remoteserver': remoteserver})


