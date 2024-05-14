from django.urls import path
from .views import unscramble_mac_view

urlpatterns = [
    path('unscramble_mac/', unscramble_mac_view, name='unscramble_mac'),
]
