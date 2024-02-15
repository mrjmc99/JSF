# sites/admin.py
from django.contrib import admin
from .models import SiteURL

@admin.register(SiteURL)
class SiteURLAdmin(admin.ModelAdmin):
    list_display = ['url', 'description']
    search_fields = ['url', 'description']
