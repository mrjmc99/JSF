# updatecontact/admin.py
from django.contrib import admin
from .models import Facility, FacilityGroup

class FacilityAdmin(admin.ModelAdmin):
    list_display = ['name', 'facility_id', 'ei_system']
    search_fields = ['name', 'facility_id']
    list_filter = ['ei_system']

admin.site.register(Facility, FacilityAdmin)

@admin.register(FacilityGroup)
class FacilityGroupAdmin(admin.ModelAdmin):
    list_display = ('name','ei_system')
    filter_horizontal = ('facilities',)
