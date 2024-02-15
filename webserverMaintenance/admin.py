# webservermaintenance/admin.py
from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import CommandLog, RemoteServer, RemoteCommand

admin.site.register(CommandLog)
admin.site.register(RemoteServer)
admin.site.register(RemoteCommand)