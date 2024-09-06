from django.urls import path
from . import views

urlpatterns = [
    path('', views.xero_imaging_bridge, name='xero_image_bridge'),
    path('<str:xero_server_slug>/', views.xero_imaging_bridge, name='xero_imaging_bridge_by_server'),
]
