# MoveEIWorkstation/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('move/', views.move_workstation, name='move_workstation'),
    path('create_workstation/', views.create_workstation, name='create_workstation'),
]
