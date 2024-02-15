from django.urls import path
from . import views

urlpatterns = [
    path('', views.search_logs, name='search_logs'),
    path('execute/', views.execute_search, name='execute_search'),  # Add this line
]
