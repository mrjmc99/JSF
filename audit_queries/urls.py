from django.urls import path
from . import views

urlpatterns = [
    path('', views.audit_query_list, name='audit_query_list'),
    path('execute/<int:query_id>/', views.execute_audit_query, name='execute_audit_query'),
]
