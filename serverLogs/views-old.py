from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
from django.http import HttpResponse
from .models import PACSCore, RemoteWindowsServer, PredefinedSearch
import smbclient
import logging
import sys
import time
from datetime import datetime, timedelta
import re

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

@permission_required('serverLogs.use_serverLogs')
def execute_search(request):
    # Get user input
    pacs_core_id = request.POST.get('core')
    free_text = request.POST.get('free_text_search')
    predefined_search_id = request.POST.get('predefined_search')

    if predefined_search_id:
        predefined_search = PredefinedSearch.objects.get(id=predefined_search_id)
        search_text = predefined_search.search_query
    else:
        search_text = free_text

    grouped_results = {}  # Dictionary to store grouped results

    # Get servers for the selected PACS core
    servers = RemoteWindowsServer.objects.filter(core_id=pacs_core_id)

    # Configure the logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Create a console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    # Create a log formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)

    # Add the console handler to the logger
    logger.addHandler(console_handler)

    # Create a list to store established connections
    open_connections = []

    # Create a list to store results
    results_list = []

    for server in servers:
        # Extract credentials
        username_password = server.credentials
        username, password = username_password.split(':')

        # Setup smbclient with the given credentials
        logger.info(f"Attempting to connect to {server.name} with IP: {server.ip_address}")
        smbclient.register_session(server.ip_address, username=username, password=password)

        try:
            # Combine the server's hostname and logs_folder to create the UNC path
            unc_path = f"\\\\{server.name}\\{server.logs_folder}"
            logger.info(f"UNC Path: {unc_path}")

            # Use unc_path when working with smbclient
            log_files = [f for f in smbclient.listdir(path=unc_path) if f.startswith('server.error')]

            # Sort log_files by file name (assuming the format is 'server.error-YYYYMMDD_HHMMSS.log')
            log_files.sort(key=lambda x: x.split('-')[1].rstrip('.log'))

            # Get the most recent two log files
            recent_log_files = log_files[-1:]

            for log_file in recent_log_files:
                full_path = unc_path + '\\' + log_file
                attempts = 3  # Number of attempts to read the file
                for attempt in range(attempts):
                    try:
                        with open(full_path, 'rb') as file_obj:  # Use 'rb' for read-only binary mode
                            content = file_obj.read().decode('utf-8', errors='ignore')
                            lines = content.splitlines()

                            for i, line in enumerate(lines):
                                if search_text in line:
                                    timestamp = extract_and_convert_timestamp(lines[i - 1])
                                    log_details = extract_log_details(line)

                                    # Use a tuple (calling_ae, called_ae) as the key for the dictionary
                                    key = (log_details['calling_ae'], log_details['called_ae'])

                                    # If the key already exists, compare the timestamps
                                    if any(entry[0] == key for entry in results_list):
                                        index = next((i for i, entry in enumerate(results_list) if entry[0] == key),
                                                     None)
                                        existing_timestamp = results_list[index][1]['timestamp']
                                        if timestamp > existing_timestamp:  # If the new timestamp is newer
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
                        break  # If successfully read, break out of the retry loop
                    except Exception as e:
                        # Log a warning and wait before retrying
                        print(f"File {log_file} is locked. Retrying in 2 seconds... ({attempt + 1}/{attempts})")
                        time.sleep(2)
                    except FileNotFoundError:
                        # Log a warning and wait before retrying
                        print(f"File {log_file} not found. Retrying in 2 seconds... ({attempt + 1}/{attempts})")
                        time.sleep(2)

                # Log the processed file name
                logger.info(f"Processed file: {log_file}")

        except Exception as e:
            logger.error(f"Failed to connect to {server.name}. Error: {e}")
            return HttpResponse("An error occurred during processing.")

    # Sort the results_list based on timestamp in descending order
    results_list.sort(key=lambda x: x[1]['timestamp'], reverse=True)
    #print(results_list)

    pacs_core = PACSCore.objects.get(id=pacs_core_id)
    pacs_core_name = pacs_core.name

    if predefined_search_id:
        predefined_search = PredefinedSearch.objects.get(id=predefined_search_id)
        search_name = predefined_search.name
    else:
        search_name = "Free Text Search"

    context = {
        'results_list': results_list,  # Update the variable name
        'pacs_core_name': pacs_core_name,
        'search_name': search_name
    }

    return render(request, 'results_template.html', context)

    #print(grouped_results)
