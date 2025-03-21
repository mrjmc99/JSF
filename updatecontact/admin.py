# updatecontact/admin.py
from django.contrib import admin
from .models import Facility, FacilityGroup, EIUser


class FacilityAdmin(admin.ModelAdmin):
    list_display = ['name', 'facility_id', 'ei_system']
    search_fields = ['name', 'facility_id']
    list_filter = ['ei_system']

admin.site.register(Facility, FacilityAdmin)

@admin.register(FacilityGroup)
class FacilityGroupAdmin(admin.ModelAdmin):
    list_display = ('name','ei_system')
    filter_horizontal = ('facilities',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:  # If editing an existing group
            form.base_fields['facilities'].queryset = Facility.objects.filter(ei_system=obj.ei_system)
        else:  # If creating a new group, show all facilities
            form.base_fields['facilities'].queryset = Facility.objects.all()
        return form

@admin.register(EIUser)
class EIUserAdmin(admin.ModelAdmin):
    list_display = ('login_name', 'profession_id', 'ei_system', 'last_updated')
    search_fields = ('login_name',)
    list_filter = ('ei_system',)
    filter_horizontal = ('facility_groups',)  # This allows a nicer UI for M2M relationships