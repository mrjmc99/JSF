# timezone_updater/views.py
from django.contrib.auth.decorators import permission_required
from django.views.decorators.cache import cache_control
from django.shortcuts import render, get_object_or_404
from .models import EISystem
from .scripts import update_timezone, search_external_system, get_token, release_token


@permission_required('timezone_updater.use_timezone_updater')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def timezone_update(request):
    current_timezone = None
    selected_ei_system = None
    device_name = None
    device_code = None
    device_updated = None
    new_timezone = None
    # Fetch the list of EISystems from the database
    ei_systems = EISystem.objects.all()
    if request.method == 'POST':
        if 'look_up_timezone' in request.POST:
            # Look up current timezone based on external system code
            exsys_code = request.POST.get('exsys_code').upper()
            selected_ei_system_name = request.POST.get('ei_systems')
            selected_ei_system = get_object_or_404(EISystem, name=selected_ei_system_name)

            # Fetch the current timezone
            get_token(selected_ei_system)
            #print(exsys_code)
            current_system_details = search_external_system(selected_ei_system, exsys_code)
            # Check if the returned JSON response is empty
            if not current_system_details:
                # Add a message indicating that the external system was not found
                not_found_message = "External system not found. Please Try Again."
                print(not_found_message)
                return render(request, 'timezone_update.html',
                              {'ei_systems': ei_systems, 'not_found_message': not_found_message})

            # Check if timezone is None, and set it to 'Not Set' in that case
            if 'timezone' in current_system_details[0] and current_system_details[0]['timezone'] is None:
                current_system_details[0]['timezone'] = 'Not Set'
            #print(current_system_details[0])
            current_timezone = current_system_details[0]['timezone']
            device_name = current_system_details[0]['name']
            device_code = current_system_details[0]['code']



            # Add debug prints
            print(f"Looked up timezone: {current_timezone}")
            print(f"Looked up Name: {device_name}")
            print(f"Looked up ExtCode: {device_code}")

            # Release Auth Token
            release_token(selected_ei_system)

        elif 'update_timezone' in request.POST:
            # set device_updating
            device_updating = True

            # Handle timezone update
            exsys_code = request.POST.get('exsys_code').upper()
            new_timezone = request.POST.get('new_timezone')
            selected_ei_system_name = request.POST.get('ei_systems')
            selected_ei_system = get_object_or_404(EISystem, name=selected_ei_system_name)

            # Fetch the current timezone
            get_token(selected_ei_system)
            current_system_details = search_external_system(selected_ei_system, exsys_code)
            device_name = current_system_details[0]['name']
            device_code = current_system_details[0]['code']

            # Call your script's update_timezone function
            update_timezone(selected_ei_system, exsys_code, new_timezone, current_system_details)
            device_updated = True

            # Release Auth Token
            release_token(selected_ei_system)
            #return render(request, 'success.html', {'exsys_code': exsys_code})
    # Reset current_timezone to None for each GET request
    else:
        current_timezone = None



    # Add debug prints
    print(f"Selected EI System: {selected_ei_system}")
    print(f"Current Timezone: {current_timezone}")

    return render(request, 'timezone_update.html', {'ei_systems': ei_systems, 'current_timezone': current_timezone, 'selected_ei_system': selected_ei_system, 'device_name': device_name,'device_updated': device_updated, 'new_timezone': new_timezone, 'device_code': device_code})