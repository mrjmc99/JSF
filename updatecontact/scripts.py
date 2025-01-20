# updatecontact/scripts.py
import logging

import requests
from django.utils.timezone import now
from updatecontact.models import Facility, EIUser


# Function to get API auth token
def get_token(ei_system):
    auth_url = f"https://{ei_system.ei_fqdn}/authentication/token"
    params = {"user": ei_system.ei_user, "password": ei_system.ei_password}

    try:
        response = requests.get(auth_url, params=params, verify=False)
        response.raise_for_status()
        token = response.text.split('CDATA[')[1].split(']]')[0]
        print("Token acquired successfully.")
        return token
    except requests.RequestException as e:
        print(f"Failed to acquire token. Error: {str(e)}")
        raise

# Function to get professional's facilities
def get_professional_details(profession_id, ei_system, TOKEN):
    response = requests.get(
        f'https://{ei_system.ei_fqdn}/ris/web/v1/contactusers/professional/{profession_id}',
        headers={"Authorization": f"Bearer {TOKEN}", "accept": "application/json"},
        verify=False
    )
    professional_data = response.json()
    return professional_data

# Function to update professional details
def update_professional_details(profession_id, ei_system, TOKEN, updated_details):
    update_url = f"https://{ei_system.ei_fqdn}/ris/web/v1/contactusers/professional/{profession_id}"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.put(update_url, headers=headers, json=updated_details, verify=False)
        response.raise_for_status()
        print("Professional details updated successfully.")
        return True
    except requests.RequestException as e:
        print(f"Failed to update professional details. Error: {str(e)}")
        return False

# Function to release token
def release_token(ei_system, TOKEN):
    print(f"Releasing token for user: {ei_system.ei_user}")
    auth_url = f"https://{ei_system.ei_fqdn}/authentication/logout"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    try:
        response = requests.get(auth_url, headers=headers, verify=False)
        response.raise_for_status()
        print("Token released successfully.")
    except requests.RequestException as e:
        print(f"Failed to release token. Error: {str(e)}")
        raise

# Function to get list of facilities from API
def get_facilities_from_api(ei_system, TOKEN):
    facilities_url = f"https://{ei_system.ei_fqdn}/ris/web/v1/facilities"
    headers = {"Authorization": f"Bearer {TOKEN}", "accept": "application/json"}

    try:
        response = requests.get(facilities_url, headers=headers, verify=False)
        response.raise_for_status()
        facilities_data = response.json()
        return facilities_data['results']
    except requests.RequestException as e:
        print(f"Failed to fetch facilities. Error: {str(e)}")
        return []


def sync_ei_user_facilities(user: EIUser,ei_system,TOKEN) -> bool:
    """
    Pushes the correct facility list for the given EIUser to the EI system.
    Returns True if successful, else False.
    """
    profession_id = user.profession_id
    login_name = user.login_name


    # 2) Fetch existing professional details
    professional_details = get_professional_details(profession_id, ei_system, TOKEN)

    # 3) Build union of group-based facilities.
    #    If you also store individually assigned facilities, add them here too.
    group_facility_ids = Facility.objects.filter(
        facilitygroup__in=user.facility_groups.all()
    ).values_list('facility_id', flat=True)

    # Convert to your desired final list of dictionaries (similar to update_facilities logic)
    updated_facilities = []
    for fac_id in group_facility_ids:
        try:
            fac_obj = Facility.objects.get(ei_system=ei_system, facility_id=fac_id)
            updated_facilities.append({
                "id": None,  # or existing if you want to reuse
                "facility": {
                    "id": fac_obj.facility_id,
                    "name": fac_obj.name
                },
                "accessType": {
                    "name": "Staff",
                    "id": 10000
                }
            })
        except Facility.DoesNotExist:
            pass

    # 4) Overwrite professionalDepartments
    professional_details['contact']['professionalDepartments'] = updated_facilities
    professional_details['contact']['shouldSave'] = True

    # 5) Push to EI
    logging.info(f"attempting to update {login_name} on {ei_system}")
    success = update_professional_details(profession_id, ei_system, TOKEN, professional_details)

    if success:
        print(f"Successful update of {login_name} on {ei_system}")
        user.last_updated = now()
        user.save(update_fields=['last_updated'])
        return True
    logging.error(f"Failed update of {login_name} on {ei_system}")
    return False
