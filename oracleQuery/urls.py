# oraclequery/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_page, name='oraclequery_main_page'),
    path('<int:query_id>/', views.execute_query_view, name='execute_query'),
]
