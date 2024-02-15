# scripts.py
import requests
TOKEN = None

# Function to get API auth token
def get_token(ei_system):
    global TOKEN
    print(f"Getting a token for user {ei_system.ei_user}")
    auth_url = f"https://{ei_system.ei_fqdn}/authentication/token"
    params = {"user": ei_system.ei_user, "password": ei_system.ei_password}

    try:
        response = requests.get(auth_url, params=params, verify=True)
        response.raise_for_status()
        TOKEN = response.text.split('CDATA[')[1].split(']]')[0]
        print("Token acquired successfully.")
    except requests.RequestException as e:
        print(f"Failed to acquire token. Error: {str(e)}")
        raise

# Function to search for external system using API call
def search_external_system(ei_system, exsys_code):
    try:
        search_url = f"https://{ei_system.ei_fqdn}/configuration/v1/externalSystems?code={exsys_code}"
        headers = {"Authorization": f"Bearer {TOKEN}"}
        #print(TOKEN)
        response = requests.get(search_url, headers=headers, verify=True)
        response.raise_for_status()
        #print(response.json())
        return response.json()
    except requests.RequestException as e:
        print(f"Failed to search for external system. Error: {str(e)}")
        raise

# Function to update timezone for external system using API call
def update_timezone(ei_system, exsys_code, new_timezone, original_system_details):
    try:
        # Extract the first element of the list
        #print(TOKEN)
        system_to_update = original_system_details[0]

        # Update the timezone field in the original JSON response
        system_to_update["timezone"] = new_timezone

        update_url = f"https://{ei_system.ei_fqdn}/configuration/v1/externalSystems/{exsys_code}"
        headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

        # Send the entire updated JSON object in the PUT request
        response = requests.put(update_url, headers=headers, json=system_to_update, verify=True)
        response.raise_for_status()

        print(f"Timezone updated successfully to {new_timezone}")
    except requests.RequestException as e:
        print(f"Failed to update timezone. Error: {str(e)}")
        raise

#function to release token
def release_token(ei_system):
    print(f"Releasing token for user: {ei_system.ei_user}")
    auth_url = f"https://{ei_system.ei_fqdn}/authentication/logout"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    try:
        response = requests.get(auth_url, headers=headers, verify=True)
        response.raise_for_status()
        print("Token released successfully.")
    except requests.RequestException as e:
        print(f"Failed to release token. Error: {str(e)}")
        raise


# Function to get and display external system details
def display_external_system_details(system):
    # Display relevant details from the API response
    print(f"Name: {system['name']}")
    print(f"Code: {system['code']}")
    print(f"Current Timezone: {system['timezone']}")
    # Add any other details you want to display
