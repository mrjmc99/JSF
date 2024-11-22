# updatecontact/scripts.py
import requests

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