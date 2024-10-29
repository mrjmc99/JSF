# updatecontact/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.search_professional, name='search_professional'),
    path('update/<int:profession_id>/', views.update_facilities, name='update_facilities'),
    path('manage-groups/', views.manage_facility_groups, name='manage_facility_groups'),
    path('refresh_facilities/<int:ei_system_id>/', views.refresh_facilities, name='refresh_facilities'),
]
