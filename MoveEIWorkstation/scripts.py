# MoveEIWorkstation/scripts.py
from django.shortcuts import get_object_or_404

from updatecontact.scripts import get_token, release_token
from timezone_updater.models import EISystem
import requests

def register_workstation(ei_system, workstation_name):
    selected_ei_system = get_object_or_404(EISystem, name=ei_system)
    token = get_token(selected_ei_system)
    register_url = f"https://{selected_ei_system.ei_fqdn}/ris/web/v1/pacsconfig/registerWorkstation"
    params = {"name": workstation_name}
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.post(register_url, params=params, headers=headers, verify=False)
        response.raise_for_status()
        release_token(selected_ei_system, token)

        # Check for empty response content
        if response.content.strip():  # If there is content, attempt to parse it
            return response.json()
        else:
            return {"status": "success", "message": "Workstation registered successfully."}

    except requests.RequestException as e:
        release_token(selected_ei_system, token)
        print(f"Failed to create workstation. Error: {e}")
        raise
