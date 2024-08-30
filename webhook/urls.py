# webhook/urls.py

from django.urls import path
from .views import webhook_listener

urlpatterns = [
    path('', webhook_listener, name='webhook_listener'),
]
