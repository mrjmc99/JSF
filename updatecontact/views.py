# updatecontact/views.py
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.utils.timezone import now
from .models import Facility, FacilityGroup, EIUserFacilityAssignment, EIUser
from .scripts import get_token, release_token, get_professional_details, update_professional_details, \
    get_facilities_from_api, sync_ei_user_facilities
import urllib3
from django.shortcuts import render, redirect, get_object_or_404
from .models import Facility
from timezone_updater.models import EISystem
import requests
import logging

logging.basicConfig(level=logging.INFO)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
TOKEN = None


# View for searching a professional
@permission_required('updatecontact.use_updatecontact')
def search_professional(request):
    professional = None
    ei_user = None  # <--- We'll pass this into the template later
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

            # Perform API call to get professional details by loginName
            response = requests.get(
                f'https://{selected_ei_system.ei_fqdn}/ris/web/v1/contactusers/querycontactusers?loginName={login_name}',
                headers={
                    "Authorization": f"Bearer {TOKEN}",
                    "accept": "application/json"
                },
                verify=False
            )

            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('total') > 0:
                        # The user exists in EI, so let's fetch details and store them.
                        professional = data['results'][0]
                        profession_id = professional['professionId']

                        professional_data = get_professional_details(profession_id, selected_ei_system, TOKEN)
                        facilities = professional_data['contact']['professionalDepartments']
                        facilities.sort(key=lambda x: x['facility']['name'])

                        assigned_facility_ids = [f['facility']['id'] for f in facilities]

                        # Filter available facilities that are NOT assigned
                        all_facilities = Facility.objects.filter(ei_system=selected_ei_system).exclude(
                            facility_id__in=assigned_facility_ids
                        ).order_by('name')

                        # Get all facility groups (those that include facilities in this EI system)
                        all_groups = FacilityGroup.objects.filter(
                            facilities__ei_system=selected_ei_system
                        ).distinct().order_by('name')

                        # Create or get a local EIUser entry to track group memberships, etc.
                        ei_user, created = EIUser.objects.get_or_create(
                            ei_system=selected_ei_system,
                            login_name=login_name,
                            profession_id=profession_id
                        )
                    else:
                        # The user was not found in EI for the given loginName
                        all_facilities = Facility.objects.filter(ei_system=selected_ei_system)
                        ei_user = None

                except requests.exceptions.JSONDecodeError:
                    logging.error("Failed to decode JSON, response text: %s", response.text)
            else:
                logging.error(f"Request failed with status code {response.status_code}: {response.text}")

            # Release token after use
            release_token(selected_ei_system, TOKEN)

    return render(request, 'search_contact.html', {
        'professional': professional,   # EI data from the API
        'facilities': facilities,       # Current assigned EI facilities
        'all_facilities': all_facilities,
        'all_groups': all_groups,
        'ei_user': ei_user,            # Local DB record (could be None if user not found in EI)
        'ei_systems': ei_systems,
        'selected_ei_system': selected_ei_system,
        'login_name': login_name,
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

        # 1) Acquire token
        TOKEN = get_token(selected_ei_system)

        # 2) Get existing professional details from EI
        professional_details = get_professional_details(profession_id, selected_ei_system, TOKEN)
        print(f'Original professional details: {professional_details}')

        # 3) Fetch or create the local EIUser so we can record group selections
        ei_user, _ = EIUser.objects.get_or_create(
            ei_system=selected_ei_system,
            profession_id=profession_id,
            login_name=login_name
        )

        # 4) Parse the group checkboxes (selected groups) and update the EIUser's local DB association
        checked_group_ids = request.POST.getlist('group_ids', [])
        ei_user.facility_groups.set(FacilityGroup.objects.filter(pk__in=checked_group_ids))

        # 5) Collect facility IDs from:
        #    a) "current" checkboxes
        #    b) "available" checkboxes
        #    c) all facilities in the user's selected groups
        current_facility_ids = request.POST.getlist('current_facilities', [])
        available_facility_ids = request.POST.getlist('available_facilities', [])

        # Convert group-based facility IDs to string, since form data is in string format
        group_facility_ids = list(
            map(
                str,  # convert int -> str
                Facility.objects.filter(
                    facilitygroup__in=ei_user.facility_groups.all()
                ).values_list('facility_id', flat=True)
            )
        )

        # Build a unique set of all facility IDs as strings
        union_facility_ids = set(
            current_facility_ids + available_facility_ids + group_facility_ids
        )

        print(f"Union of all facility IDs: {union_facility_ids}")

        # 6) Build updated list of professionalDepartments
        updated_facilities = []

        # 6a) First, reuse any existing departments from professional_details if they match the union
        existing_departments = professional_details['contact'].get('professionalDepartments', [])
        for existing_dept in existing_departments:
            existing_id_str = str(existing_dept['facility']['id'])
            if existing_id_str in union_facility_ids:
                # Keep it and remove from union so we don't add it again as new
                updated_facilities.append(existing_dept)
                union_facility_ids.remove(existing_id_str)

        # 6b) Now add new entries for any facility IDs still in union_facility_ids
        #     that weren't in the existing departments
        for facility_id_str in union_facility_ids:
            try:
                facility_obj = Facility.objects.get(
                    facility_id=int(facility_id_str),
                    ei_system=selected_ei_system
                )
                updated_facilities.append({
                    'id': None,  # signals EI to create a new record
                    'facility': {
                        'id': facility_obj.facility_id,
                        'name': facility_obj.name
                    },
                    'accessType': {
                        'name': 'Staff',  # default or adjust as necessary
                        'id': 10000       # default or adjust as necessary
                    }
                })
            except Facility.DoesNotExist:
                logging.error(
                    f"Facility with ID={facility_id_str} not found in the database "
                    f"for EI system {selected_ei_system}."
                )

        # 6c) Overwrite professionalDepartments with our new list
        professional_details['contact']['professionalDepartments'] = updated_facilities
        professional_details['contact']['shouldSave'] = True
        print(f'Updated professional details: {professional_details}')

        # 7) Push updates to EI
        update_success = update_professional_details(
            profession_id, selected_ei_system, TOKEN, professional_details
        )

        # 8) Release token
        release_token(selected_ei_system, TOKEN)

        if update_success:
            logging.info("Professional facilities updated successfully.")
            ei_user.last_updated = now()
            ei_user.save(update_fields=['last_updated'])
        else:
            logging.error("Failed to update professional facilities.")

        # 9) Redirect back to search page
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

    ei_system_id = request.GET.get('ei_system_id')
    if ei_system_id:
        try:
            selected_ei_system = get_object_or_404(EISystem, pk=int(ei_system_id))
            facility_groups = FacilityGroup.objects.filter(ei_system=selected_ei_system).order_by('name')
        except ValueError:
            selected_ei_system = None

    group_id = request.GET.get('group_id')
    if group_id:
        try:
            selected_group = get_object_or_404(FacilityGroup, pk=int(group_id))
        except ValueError:
            selected_group = None

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
                    selected_facility_ids = set(map(int, request.POST.getlist("facilities")))

                    current_facility_ids = set(group.facilities.values_list("id", flat=True))
                    new_facility_ids = selected_facility_ids - current_facility_ids
                    removed_facility_ids = current_facility_ids - selected_facility_ids

                    group.facilities.set(Facility.objects.filter(id__in=selected_facility_ids))
                    group.save()
                    messages.success(request, f"Updated facilities for group: {group.name}")

                    # Find users assigned to this group
                    affected_users = EIUser.objects.filter(facility_groups=group).distinct()

                    if affected_users:
                        TOKEN = get_token(ei_system)
                        # Provide feedback on how many users we’re going to sync
                        messages.info(request, f"Syncing {affected_users.count()} user(s) to EI...")

                        successful_count = 0
                        failed_count = 0

                        # Sync each user
                        for user in affected_users:
                            success = sync_ei_user_facilities(user, ei_system, TOKEN)
                            if success:
                                successful_count += 1
                            else:
                                failed_count += 1

                        # Provide a final summary to the user
                        if successful_count > 0:
                            messages.success(request, f"Successfully synced {successful_count} user(s).")
                        if failed_count > 0:
                            messages.error(request, f"Failed to sync {failed_count} user(s).")
                        release_token(ei_system,TOKEN)

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



