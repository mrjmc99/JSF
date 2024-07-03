#ei_status\views.py
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, redirect
from django import forms
from django.views.decorators.cache import cache_control
from requests import Timeout
from django.utils import timezone
from timezone_updater.models import EISystem
import requests
import re
import logging
import socket
import time

# Form to select the EISystem
class EISystemForm(forms.Form):
    ei_system = forms.ModelChoiceField(queryset=EISystem.objects.all(), label="Select EI System")

# Function to get auth token
def get_token(ei_system):
    global TOKEN
    auth_url = f"https://{ei_system.ei_fqdn}/authentication/token"
    params = {"user": ei_system.ei_user, "password": ei_system.ei_password}

    try:
        response = requests.get(auth_url, params=params, verify=True)
        response.raise_for_status()
        TOKEN = response.text.split('CDATA[')[1].split(']]')[0]
    except requests.RequestException as e:
        raise Exception(f"Failed to acquire token. Error: {str(e)}")

# Function to release token
def release_token(ei_system):
    auth_url = f"https://{ei_system.ei_fqdn}/authentication/logout"
    headers = {"Authorization": f"Bearer {TOKEN}"}

    try:
        response = requests.get(auth_url, headers=headers, verify=True)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Failed to release token. Error: {str(e)}")


def check_cluster_node_health(ip_address, max_retries=2):
    health_url = f"https://{ip_address}/status"
    retries = 0

    while retries <= max_retries:
        try:
            response = requests.get(health_url, timeout=2, verify=0)
            response.raise_for_status()
            health_status = response.text.strip()
            print(f"Node {ip_address}: {response.status_code} - {response.text.strip()}")
            return health_status, retries  # Return health status and number of retries
        except Timeout:
            health_status = "Unavailable: (Starting, Stopping or Unresponsive)"
            print(f"Node {ip_address}: Timeout")
        except requests.RequestException as e:
            health_status = f"Unavailable: (Starting, Stopping or Unresponsive) {str(e)}"
            print(f"Node {ip_address}: Error - {str(e)}")

        retries += 1
        time.sleep(1)  # Wait for 1 second before retrying

    # If max retries exceeded
    return health_status, retries


def call_cluster_api(ei_system):
    get_token(ei_system)
    headers = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/json"}
    cluster_url = f"https://{ei_system.ei_fqdn}/ris/web/v2/queues/availableNodes"

    try:
        response = requests.get(cluster_url, headers=headers, verify=True)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logging.error(f"API call failed. Error: {str(e)}")
        return None
    finally:
        release_token(ei_system)

def check_cluster_nodes(cluster_nodes):
    nodes = re.findall(r'\b\d+\.\d+\.\d+\.\d+\b', cluster_nodes)
    statuses = []

    for node in nodes:
        ip_address = node
        try:
            hostname, _, _ = socket.gethostbyaddr(ip_address)
            if '.' in hostname:
                hostname = hostname.split('.')[0]
        except (socket.herror, socket.gaierror):
            hostname = "Unknown"

        health_status,retries = check_cluster_node_health(ip_address)
        statuses.append((ip_address, hostname, health_status, retries))

    return statuses


@permission_required('ei_status.use_ei_status')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def index(request):
    if request.method == "POST":
        form = EISystemForm(request.POST)
        if form.is_valid():
            ei_system = form.cleaned_data['ei_system']
            cluster_nodes = call_cluster_api(ei_system)
            if cluster_nodes:
                statuses = check_cluster_nodes(cluster_nodes)
                return render(request, 'status_page.html', {
                    'statuses': statuses,
                    'ei_system': ei_system,
                    'current_time': timezone.now(),
                    'cluster_nodes': cluster_nodes,
                })
    else:
        # Prepopulate the form with the first EISystem instance
        first_ei_system = EISystem.objects.first()
        form = EISystemForm(initial={'ei_system': first_ei_system})

    return render(request, 'index.html', {'form': form})
