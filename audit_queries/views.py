# audit_queries/views.py
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import AuditQuery, SubQuery
from django.db import connections
from django.contrib.auth.decorators import login_required,permission_required
import json
import logging

@permission_required('audit_queries.use_audit_queries')
def audit_query_list(request):
    """
    Display a list of available audit queries.
    """
    queries = AuditQuery.objects.all()
    return render(request, 'list.html', {'queries': queries})


@permission_required('audit_queries.use_audit_queries')
def execute_audit_query(request, query_id):
    """
    Execute a specific audit query and display its results.
    """
    try:
        query = AuditQuery.objects.get(id=query_id)
    except AuditQuery.DoesNotExist:
        return render(request, 'error.html', {'message': 'Audit Query not found'})

    # Extract variables and user inputs
    variables_dict = query.variables or {}
    variables = variables_dict.get("variables", [])

    params = {}
    for variable in variables:
        if variable['type'] == 'date':
            date_str = request.GET.get(variable['name'])
            date_obj = datetime.strptime(date_str, '%Y-m-d H:i')
            epoch_time = int((date_obj - datetime(1970, 1, 1)).total_seconds())
            params[variable['name']] = epoch_time
        else:
            params[variable['name']] = request.GET.get(variable['name'])

    #print(f"Initial parameters: {params}")  # Log initial parameters

    # If the query requires a preliminary query, execute it first
    if query.requires_preliminary:
        with connections[query.preliminary_db.db_alias].cursor() as cursor:
            #print(f"Executing preliminary query: {query.preliminary_query}")  # Log preliminary query
            cursor.execute(query.preliminary_query, params)
            result = cursor.fetchone()
            if result:
                params["study_ref"] = result[0]
                #print(f"Updated parameters after preliminary query: {params}")  # Log updated parameters
            else:
                return render(request, 'error.html', {'message': 'Preliminary data not found'})

    results = []
    columns = []

    # Execute the main query
    with connections[query.database.db_alias].cursor() as cursor:
        #print(f"Executing main query: {query.query}")  # Log main query
        cursor.execute(query.query, params)
        results.extend(cursor.fetchall())
        columns = [col[0] for col in cursor.description]

    # Execute subqueries, if any
    subqueries = SubQuery.objects.filter(parent_query=query)

    for subquery in subqueries:
        with connections[subquery.database.db_alias].cursor() as cursor:
            #print(f"Executing subquery: {subquery.query}")  # Log subquery
            cursor.execute(subquery.query, params)
            results.extend(cursor.fetchall())
            # Ensure that columns are consistent across main query and subqueries
            if not columns:
                columns = [col[0] for col in cursor.description]

    page_title = f"{query.name}"

    return render(request, 'conversion_results.html', {
        'columns': columns,
        'results': results,
        'page_title': page_title,
        'params': params  # Passing the collected variable values
    })






@permission_required('audit_queries.use_audit_queries')
def fetch_audit_data(query, server):
    """
    Fetch data for an audit query.
    """
    with connections[server].cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
    return rows

