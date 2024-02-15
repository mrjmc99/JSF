# timezone_updater/admin.py

from django.contrib import admin
from .models import EISystem


@admin.register(EISystem)
class EISystemAdmin(admin.ModelAdmin):
    list_display = ('name', 'ei_fqdn', 'ei_user')
