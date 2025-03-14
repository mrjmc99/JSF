#serverlogs/views.py
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
from concurrent.futures import ThreadPoolExecutor
from django.http import HttpResponse
from .models import PACSCore, RemoteWindowsServer, PredefinedSearch, RemoteLinuxServer
import smbclient
import logging
import sys
import time
from datetime import datetime, timedelta
import re
import paramiko
import os
import io
import posixpath

# Configure the logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

# Create a console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.ERROR)

# Create a log formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Add the console handler to the logger
logger.addHandler(console_handler)

# Create a file handler
file_handler = logging.FileHandler('D:\web\JSF\logfile.log')  # Specify the path to your log file
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)



@permission_required('serverLogs.use_serverLogs')
def search_logs(request):
    cores = PACSCore.objects.all()
    predefined_searches = PredefinedSearch.objects.all()

    context = {
        'cores': cores,
        'predefined_searches': predefined_searches
    }

    return render(request, 'search_logs.html', context)

#@permission_required('serverLogs.use_serverLogs')
def extract_log_details(log_message):
    reason_pattern = re.compile(r"reason: (\d+ - [\w-]+)")
    calling_ae_pattern = re.compile(r"Calling AE info \[([\w]+)")
    called_ae_pattern = re.compile(r"Called AE info \[([\w]+)\]")

    reason = reason_pattern.search(log_message)
    calling_ae = calling_ae_pattern.search(log_message)
    called_ae = called_ae_pattern.search(log_message)

    details = {
        'reason': reason.group(1) if reason else '',
        'calling_ae': calling_ae.group(1) if calling_ae else '',
        'called_ae': called_ae.group(1) if called_ae else ''
    }

    return details

#@permission_required('serverLogs.use_serverLogs')
def extract_and_convert_timestamp(timestamp_line):
    time_start = timestamp_line.find('time="') + 6
    time_end = timestamp_line.find('"', time_start)

    if time_start != -1 and time_end != -1:
        timestamp = timestamp_line[time_start:time_end]

        dt_format = "%Y/%m/%d %H:%M:%S.%f"
        utc_dt = datetime.strptime(timestamp[:-6], dt_format)
        offset_minutes = int((datetime.utcnow() - datetime.now()).total_seconds() / 60)
        local_dt = utc_dt - timedelta(minutes=offset_minutes)

        local_timestamp = local_dt.strftime(dt_format)

        # Ensure consistent formatting for sorting
        return local_timestamp
    return None


# Helper function to process log file
def process_log_file(log_file_path, search_pattern, results_list, is_specific_search=False):
    attempts = 3

    for attempt in range(attempts):
        try:
            with open(log_file_path, 'rb') as file_obj:
                content = file_obj.read().decode('utf-8', errors='ignore')
                lines = content.splitlines()

                for i, line in enumerate(lines):
                    if re.search(search_pattern, line):
                        timestamp = extract_and_convert_timestamp(lines[i - 1])

                        if is_specific_search:
                            log_details = extract_log_details(line)

                            key = (log_details['calling_ae'], log_details['called_ae'])

                            if any(entry[0] == key for entry in results_list):
                                index = next((i for i, entry in enumerate(results_list) if entry[0] == key), None)
                                existing_timestamp = results_list[index][1]['timestamp']
                                if timestamp > existing_timestamp:
                                    results_list[index] = ((key, {
                                        'timestamp': timestamp,
                                        'reason': log_details['reason'],
                                        'calling_ae': log_details['calling_ae'] or "Unknown AE",
                                        'called_ae': log_details['called_ae'] or "Unknown AE",
                                    }))
                            else:
                                results_list.append((key, {
                                    'timestamp': timestamp,
                                    'reason': log_details['reason'],
                                    'calling_ae': log_details['calling_ae'] or "Unknown AE",
                                    'called_ae': log_details['called_ae'] or "Unknown AE",
                                }))
                        else:
                            results_list.append((timestamp, line))

            break
        except Exception as e:
            print(f"Error reading log file {log_file_path}: {e}")
            time.sleep(2)
        except FileNotFoundError:
            print(f"File {log_file_path} not found. Retrying in 2 seconds... ({attempt + 1}/{attempts})")
            time.sleep(2)


# Helper function to process a single server
def process_server(server, search_pattern, results_list, is_specific_search=False):
    username_password = server.credentials
    username, password = username_password.split(':')

    print(f"Attempting to connect to {server.name} with IP: {server.ip_address}")
    smbclient.register_session(server.ip_address, username=username, password=password)

    try:
        unc_path = f"\\\\{server.name}\\{server.logs_folder}"
        print(f"UNC Path: {unc_path}")

        log_files = [f for f in smbclient.listdir(path=unc_path) if f.startswith('server.error')]

        log_files.sort(key=lambda x: x.split('-')[1].rstrip('.log'))

        recent_log_files = log_files[-1:]

        for log_file in recent_log_files:
            full_path = unc_path + '\\' + log_file
            process_log_file(full_path, search_pattern, results_list, is_specific_search)

            print(f"Processed file: {log_file}")

    except Exception as e:
        print(f"Failed to connect to {server.name}. Error: {e}")
    finally:
        smbclient.reset_connection_cache()


def process_server_linux(server, search_pattern, results_list, is_specific_search=False):
    ssh_username = server.ssh_username
    # Use the ssh_key_path from the model; if not set, the default is already provided.
    private_key_path = server.ssh_key_path

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"Connecting to {server.name} at {server.ip_address} via SSH using key file {private_key_path}")
        client.connect(server.ip_address, username=ssh_username, key_filename=private_key_path)
        sftp = client.open_sftp()

        remote_dir = server.logs_folder
        log_files = [f for f in sftp.listdir(remote_dir) if f.startswith('server.error')]

        # Sort the log files (customize this sort key as needed)
        log_files.sort(key=lambda x: x.split('-')[1].rstrip('.log'))
        recent_log_files = log_files[-1:]

        for log_file in recent_log_files:
            full_path = posixpath.join(remote_dir, log_file)
            print(f"Processing file: {full_path}")
            try:
                with sftp.file(full_path, 'r') as file_obj:
                    content = file_obj.read().decode('utf-8', errors='ignore')
                    lines = content.splitlines()

                    for i, line in enumerate(lines):
                        if re.search(search_pattern, line):
                            timestamp = extract_and_convert_timestamp(lines[i - 1])
                            if is_specific_search:
                                log_details = extract_log_details(line)
                                key = (log_details['calling_ae'], log_details['called_ae'])
                                if any(entry[0] == key for entry in results_list):
                                    index = next((i for i, entry in enumerate(results_list) if entry[0] == key), None)
                                    existing_timestamp = results_list[index][1]['timestamp']
                                    if timestamp > existing_timestamp:
                                        results_list[index] = (key, {
                                            'timestamp': timestamp,
                                            'reason': log_details['reason'],
                                            'calling_ae': log_details['calling_ae'] or "Unknown AE",
                                            'called_ae': log_details['called_ae'] or "Unknown AE",
                                        })
                                else:
                                    results_list.append((key, {
                                        'timestamp': timestamp,
                                        'reason': log_details['reason'],
                                        'calling_ae': log_details['calling_ae'] or "Unknown AE",
                                        'called_ae': log_details['called_ae'] or "Unknown AE",
                                    }))
                            else:
                                results_list.append((timestamp, line))
            except Exception as file_e:
                print(f"Error processing file {full_path}: {file_e}")
    except Exception as e:
        print(f"Failed to connect to {server.name}: {e}")
    finally:
        client.close()


# Main function to execute search
@permission_required('serverLogs.use_serverLogs')
def execute_search(request):
    pacs_core_id = request.POST.get('core')
    free_text = request.POST.get('free_text_search')
    predefined_search_id = request.POST.get('predefined_search')

    if predefined_search_id:
        predefined_search = PredefinedSearch.objects.get(id=predefined_search_id)
        search_pattern = predefined_search.search_query
        is_specific_search = (predefined_search.name == "Search for Rejected Modalities")
    else:
        search_pattern = free_text
        is_specific_search = False

    pacs_core = PACSCore.objects.get(id=pacs_core_id)
    pacs_core_name = pacs_core.name

    # Select server type based on the PACS core's setting.
    results_list = []
    with ThreadPoolExecutor() as executor:
        if pacs_core.server_type == 'linux':
            servers = RemoteLinuxServer.objects.filter(core=pacs_core)
            for server in servers:
                executor.submit(process_server_linux, server, search_pattern, results_list, is_specific_search)
        else:  # Default to Windows if not Linux
            servers = RemoteWindowsServer.objects.filter(core=pacs_core)
            for server in servers:
                executor.submit(process_server, server, search_pattern, results_list, is_specific_search)

    # Sorting logic remains the same
    if is_specific_search:
        results_list.sort(key=lambda x: x[1]['timestamp'], reverse=True)
    else:
        results_list.sort(key=lambda x: x[1]['timestamp'] if isinstance(x, tuple) and len(x) > 1 else '0', reverse=True)

    if predefined_search_id:
        search_name = predefined_search.name
    else:
        search_name = "Free Text Search"

    context = {
        'results_list': results_list,
        'pacs_core_name': pacs_core_name,
        'search_name': search_name,
        'is_specific_search': is_specific_search
    }
    return render(request, 'results_template.html', context)


