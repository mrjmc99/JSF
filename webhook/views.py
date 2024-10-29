# webhook/views.py

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from timezone_updater.scripts import get_token, release_token
from webhook.scripts import get_study_details, route_series
import json
ei_system = 'mivcsptest2.adventhealth.com'
external_system = ''
TOKEN = None


@csrf_exempt  # Disable CSRF protection for this view (use with caution)
def webhook_route_by_series(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Parse the JSON data from the request body
            print("Received webhook data:", data)
            # Extracting the StudyUIDs and splitting by comma
            study_uids = data.get('StudyUIDs', '').split(',')
            # Getting the first StudyUID
            study_uid = study_uids if study_uids else None
            # Printing the first StudyUID
            print(f"First StudyUID: {study_uid}")
            get_token(ei_system)
            study_details = get_study_details(study_uid, ei_system)
            series_uids = study_details.get("series", [])
            for series_uid in series_uids:
                route_series(series_uid,ei_system,external_system)
            release_token(ei_system)
            return JsonResponse({"message": "Webhook received!"}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    else:
        return JsonResponse({"error": "Invalid method"}, status=405)



@csrf_exempt  # Disable CSRF protection for this view (use with caution)
def webhook_listener(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Parse the JSON data from the request body
            print("Received webhook data:", data)
            return JsonResponse({"message": "Webhook received!"}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    else:
        return JsonResponse({"error": "Invalid method"}, status=405)

