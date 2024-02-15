# sites/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='sites_index'),
]
