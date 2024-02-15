# oraclequery/views.py
from django.shortcuts import render
from .utils import fetch_data  # import the function you created
from django.db import connections
from .models import SavedQuery, FriendlyDBName
from django.conf import settings
from datetime import datetime
from django.contrib.auth.decorators import login_required,permission_required
import json
@permission_required('oracleQuery.use_oracle_queries')
def execute_query_view(request, query_id):
    try:
        query = SavedQuery.objects.get(id=query_id)
    except SavedQuery.DoesNotExist:
        return render(request, 'error.html', {'message': 'Query not found'})

    server_id = request.GET.get('server')
    # Fetch the human-readable date from the request parameters
    human_readable_date = request.GET.get('epochTime')

    variables_dict = query.variables or {}
    variables = variables_dict.get("variables", [])

    params = {}
    for variable in variables:
        if variable['type'] == 'date':
            # Convert date string to epoch time
            date_str = request.GET.get(variable['name'])
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')  # Assuming date_str format is 'YYYY-MM-DD'
            epoch_time = int((date_obj - datetime(1970, 1, 1)).total_seconds())
            params[variable['name']] = epoch_time
        else:
            params[variable['name']] = request.GET.get(variable['name'])

    with connections[server_id].cursor() as cursor:
        cursor.execute(query.query, params)
        results = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        friendly_server_name = FriendlyDBName.objects.filter(db_alias=server_id).first().friendly_name
        page_title = f"{query.name} on {friendly_server_name}"

    return render(request, 'query_results.html', {'columns': columns, 'results': results, 'page_title': page_title, 'human_readable_date': human_readable_date})


@permission_required('oracleQuery.use_oracle_queries')
def main_page(request):
    queries = SavedQuery.objects.all()
    friendly_names = {obj.db_alias: obj.friendly_name for obj in FriendlyDBName.objects.all()}
    servers = [{'db_alias': key, 'friendly_name': friendly_names.get(key, key), 'query_type': 'impax' if 'impax' in key else 'ei'} for key in settings.DATABASES.keys() if key != 'default']

    for query in queries:
        query.variables = json.dumps(query.variables)

    return render(request, 'oraclequery_main_page.html', {'queries': queries, 'servers': servers})



@permission_required('oracleQuery.use_oracle_queries')
def execute_query(request):
    query_id = request.GET.get('query')
    server_id = request.GET.get('server')

    query = SavedQuery.objects.get(id=query_id).query
    server = RemoteServer.objects.get(id=server_id)

    # Fetch user-inputted variables
    variables = json.loads(SavedQuery.objects.get(id=query_id).variables)
    params = {}
    for variable in variables:
        params[variable['name']] = request.GET.get(variable['name'])

    results = fetch_data(query, params)

    return JsonResponse({'results': results})
@permission_required('oracleQuery.use_oracle_queries')
def fetch_data(query, server):
    with connections[server].cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
    return rows


