# timezone_updater/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.timezone_update, name='timezone_updater'),
    path('timezone_update/', views.timezone_update, name='timezone_update'),
    # Add other URL patterns as needed
]
