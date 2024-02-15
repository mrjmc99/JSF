# mainapp/admin.py
from django.contrib import admin
from .models import AppLink

class AppLinkAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'visible')
    list_editable = ('visible',)

admin.site.register(AppLink, AppLinkAdmin)
