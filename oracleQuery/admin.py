
from django.contrib import admin
from .models import SavedQuery, FriendlyDBName


admin.site.register(SavedQuery)
admin.site.register(FriendlyDBName)