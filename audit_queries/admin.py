from django.contrib import admin
from .models import AuditQuery,SubQuery

@admin.register(AuditQuery)
class AuditQueryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at', 'updated_at', 'database','requires_preliminary', 'preliminary_query', 'preliminary_db']
    search_fields = ['name', 'description']


@admin.register(SubQuery)
class SubQueryAdmin(admin.ModelAdmin):
    list_display = ('parent_query', 'query', 'database', 'order')
    list_filter = ('parent_query', 'database')
    search_fields = ('query',)
    ordering = ('parent_query', 'order')

