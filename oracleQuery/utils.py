# utils.py or in your views.py
from django.db import connections

def fetch_data(query):
    with connections['oracle_db'].cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
    return rows
