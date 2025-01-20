from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from .models import Facility, FacilityGroup
from .scripts import get_token, release_token, get_professional_details, update_professional_details, get_facilities_from_api
import urllib3
from django.shortcuts import render, redirect, get_object_or_404
from .models import Facility
from timezone_updater.models import EISystem
import requests
import logging

logging.basicConfig(level=logging.DEBUG)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
TOKEN = None


# View for searching a professional
@permission_required('updatecontact.use_updatecontact')
def search_professional(request):
    professional = None
    facilities = []
    all_facilities = []
    all_groups = []
    ei_systems = EISystem.objects.all()
    selected_ei_system = None
    login_name = ""

    if request.method == "GET" and 'login_name' in request.GET:
        login_name = request.GET['login_name']
        selected_ei_system_name = request.GET.get('ei_systems')

        if selected_ei_system_name:
            selected_ei_system = get_object_or_404(EISystem, name=selected_ei_system_name)

            # Obtain token for the selected EI system
            TOKEN = get_token(selected_ei_system)

            # Perform API call to get professional details
            response = requests.get(
                f'https://{selected_ei_system.ei_fqdn}/ris/web/v1/contactusers/querycontactusers?loginName={login_name}',
                headers={
                    "Authorization": f"Bearer {TOKEN}",
                    "accept": "application/json"
                },
                verify=False
            )

            # Check if there is a response status code and content
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('total') > 0:
                        professional = data['results'][0]
                        professional_data = get_professional_details(professional['professionId'], selected_ei_system, TOKEN)
                        facilities = professional_data['contact']['professionalDepartments']
                        facilities.sort(key=lambda x: x['facility']['name'])
                        assigned_facility_ids = [facility['facility']['id'] for facility in facilities]

                        # Filter available facilities that are not already assigned
                        all_facilities = Facility.objects.filter(ei_system=selected_ei_system).exclude(
                            facility_id__in=assigned_facility_ids
                        ).order_by('name')
                        # Get all facility groups for the selected EI system
                        all_groups = FacilityGroup.objects.filter(facilities__ei_system=selected_ei_system).distinct().order_by('name')
                    else:
                        all_facilities = Facility.objects.filter(ei_system=selected_ei_system)

                except requests.exceptions.JSONDecodeError:
                    logging.error("Failed to decode JSON, response text:", response.text)
            else:
                logging.error(f"Request failed with status code {response.status_code}: {response.text}")

            # Release token after use
            release_token(selected_ei_system, TOKEN)

    return render(request, 'search_contact.html', {
        'professional': professional,
        'facilities': facilities,
        'all_facilities': all_facilities,
        'ei_systems': ei_systems,
        'selected_ei_system': selected_ei_system,
        'login_name': login_name,
        'all_groups': all_groups,
    })




# View to refresh facilities from API
@permission_required('updatecontact.use_updatecontact')
def refresh_facilities(request, ei_system_id):
    selected_ei_system = get_object_or_404(EISystem, pk=ei_system_id)

    # Get token
    TOKEN = get_token(selected_ei_system)
    print(f"refreshing facilities for {ei_system_id}")

    # Call the API to retrieve the list of facilities for the selected EI system
    response = requests.get(
        f'https://{selected_ei_system.ei_fqdn}/ris/web/v1/contactusers/facilities',
        headers={"Authorization": f"Bearer {TOKEN}", "accept": "application/json"},
        verify=False
    )

    if response.status_code == 200:
        facilities_data = response.json()
        print(f'unfiltered:{facilities_data}')
        filtered_facilities = [facility for facility in facilities_data if facility['name'].startswith(('AH', 'Adv'))]
        print(f'filtered:{filtered_facilities}')

        # Update existing facilities or create new ones
        existing_facilities = Facility.objects.filter(ei_system=selected_ei_system)
        existing_facility_ids = {facility.facility_id for facility in existing_facilities}

        for facility in filtered_facilities:
            if facility['id'] in existing_facility_ids:
                # Update existing facility
                Facility.objects.filter(facility_id=facility['id'], ei_system=selected_ei_system).update(
                    name=facility['name']
                )
            else:
                # Create new facility
                Facility.objects.create(
                    name=facility['name'],
                    facility_id=facility['id'],
                    ei_system=selected_ei_system
                )

        messages.success(request, "Facilities refreshed successfully.")
    else:
        messages.error(request, f"Failed to refresh facilities. Status code: {response.status_code}")

    # Release token
    release_token(selected_ei_system, TOKEN)

    # Redirect back to the referring page
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('search_professional')))


# View for updating facilities
@permission_required('updatecontact.use_updatecontact')
def update_facilities(request, profession_id):
    if request.method == 'POST':
        selected_ei_system_name = request.POST.get('ei_systems')
        selected_ei_system = get_object_or_404(EISystem, name=selected_ei_system_name)
        login_name = request.POST.get('login_name')
        # Get token
        TOKEN = get_token(selected_ei_system)

        # Get the existing professional details
        professional_details = get_professional_details(profession_id, selected_ei_system, TOKEN)
        print(f'Original professional details: {professional_details}')

        # Get the current and newly added facilities from form submission
        current_facility_ids = request.POST.getlist('current_facilities')
        available_facility_ids = request.POST.getlist('available_facilities')

        print(f'Current Facility IDs from Form: {current_facility_ids}')
        print(f'Available Facility IDs from Form: {available_facility_ids}')

        # Create updated list of professionalDepartments
        updated_facilities = []

        # Append current facilities that are still selected
        for facility_id in current_facility_ids:
            matching_facility = next(
                (f for f in professional_details['contact']['professionalDepartments'] if str(f['facility']['id']) == facility_id), None
            )
            if matching_facility:
                updated_facilities.append(matching_facility)

        # Add newly selected available facilities
        for facility_id in available_facility_ids:
            # Make sure it's not already in the current facilities
            if not any(f['facility']['id'] == int(facility_id) for f in updated_facilities):
                try:
                    facility = Facility.objects.get(facility_id=facility_id, ei_system=selected_ei_system)
                    updated_facilities.append({
                        'id': None,  # Assign None or a new sequential ID if necessary
                        'facility': {
                            'id': facility.facility_id,
                            'name': facility.name
                        },
                        'accessType': {
                            'name': 'Staff',  # Default value, adjust as necessary
                            'id': 10000  # Default value, adjust as necessary
                        }
                    })
                except Facility.DoesNotExist:
                    logging.error(f"Facility with ID {facility_id} not found in the database.")

        # Update the professional details with the new facilities and set shouldSave to true
        professional_details['contact']['professionalDepartments'] = updated_facilities
        professional_details['contact']['shouldSave'] = True
        print(f'Updated professional details: {professional_details}')

        # Perform API call to update professional details
        update_success = update_professional_details(profession_id, selected_ei_system, TOKEN, professional_details)

        # Release token after use
        release_token(selected_ei_system, TOKEN)

        if update_success:
            logging.info("Professional facilities updated successfully.")
        else:
            logging.error("Failed to update professional facilities.")

        # Redirect back to the search page with the selected EI system and login name as query parameters
        query_params = f"?ei_systems={selected_ei_system_name}&login_name={login_name}"
        return HttpResponseRedirect(reverse('search_professional') + query_params)






# View for managing facility groups
@permission_required('updatecontact.use_updatecontact')
def manage_facility_groups(request):
    ei_systems = EISystem.objects.all()
    selected_ei_system = None
    selected_group = None
    facility_groups = []
    assigned_facilities = []
    available_facilities = []

    # Check if 'ei_system_id' is provided in GET request
    ei_system_id = request.GET.get('ei_system_id')
    if ei_system_id:
        try:
            selected_ei_system = get_object_or_404(EISystem, pk=int(ei_system_id))
            facility_groups = FacilityGroup.objects.filter(ei_system=selected_ei_system).order_by('name')
        except ValueError:
            selected_ei_system = None  # If invalid ID, reset selection

    # Check if 'group_id' is provided in GET request
    group_id = request.GET.get('group_id')
    if group_id:
        try:
            selected_group = get_object_or_404(FacilityGroup, pk=int(group_id))
        except ValueError:
            selected_group = None  # Reset selection if invalid

    if selected_group:
        assigned_facilities = selected_group.facilities.all().order_by('name')
        available_facilities = Facility.objects.filter(ei_system=selected_group.ei_system).exclude(
            id__in=assigned_facilities.values_list('id', flat=True)
        ).order_by('name')

    if request.method == "POST":
        ei_system_id = request.POST.get("ei_system_id")
        action = request.POST.get("action")

        if ei_system_id:
            ei_system = get_object_or_404(EISystem, pk=ei_system_id)

            if action == "update_groups":
                group_id = request.POST.get("group_id")
                if group_id:
                    group = get_object_or_404(FacilityGroup, id=group_id)
                    selected_facility_ids = request.POST.getlist("facilities")

                    group.facilities.set(Facility.objects.filter(id__in=selected_facility_ids))
                    messages.success(request, f"Updated facilities for group: {group.name}")

            elif action == "create_group":
                new_group_name = request.POST.get("new_group_name")
                if new_group_name:
                    new_group = FacilityGroup.objects.create(name=new_group_name, ei_system=ei_system)
                    messages.success(request, f"Created new facility group: {new_group.name}")
                    return redirect(f"{request.path}?ei_system_id={ei_system.id}&group_id={new_group.id}")

        return redirect(f"{request.path}?ei_system_id={ei_system_id if ei_system_id else ''}&group_id={group_id if action == 'update_groups' else ''}")

    return render(request, 'manage_groups.html', {
        "ei_systems": ei_systems,
        "selected_ei_system": selected_ei_system,
        "selected_group": selected_group,
        "facility_groups": facility_groups,
        "assigned_facilities": assigned_facilities,
        "available_facilities": available_facilities,
    })


