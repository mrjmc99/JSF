# serverlogs/admin
from django.contrib import admin
from .models import PACSCore, RemoteWindowsServer, PredefinedSearch

@admin.register(PACSCore)
class PACSCoreAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(RemoteWindowsServer)
class RemoteWindowsServerAdmin(admin.ModelAdmin):
    list_display = ['name', 'ip_address', 'logs_folder', 'core']
    list_filter = ['core']
    search_fields = ['name', 'ip_address']


@admin.register(PredefinedSearch)
class PredefinedSearchAdmin(admin.ModelAdmin):
    list_display = ['name', 'search_query']
    search_fields = ['name']
