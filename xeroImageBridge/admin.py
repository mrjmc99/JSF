from django.contrib import admin

# Register your models here.
from .models import XeroConfig

@admin.register(XeroConfig)
class XeroConfigAdmin(admin.ModelAdmin):
    list_display = ('xero_server', 'xero_user', 'xero_domain')