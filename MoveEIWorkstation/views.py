# MoveEIWorkstation/views.py
from django.http import JsonResponse
from django.shortcuts import render
from django.db import connections
from .forms import WorkstationForm
from django.contrib.auth.decorators import permission_required

@permission_required('moveEIWorkstation.use_move_ei_workstations')
def move_workstation(request):
    workstation = None
    response_data = {}

    if request.method == 'POST':
        form = WorkstationForm(request.POST)

        if form.is_valid():
            db_alias = form.cleaned_data['db_alias']
            workstation_name = form.cleaned_data['workstation_name']
            new_group = form.cleaned_data['new_group']

            # Execute workstation search
            with connections[db_alias].cursor() as cursor:
                cursor.execute("""
                    SELECT loc.name as WSGName, ws.WORKSTATION_GROUP, ws.id as workstation_id, 
                           ws.name as workstation, ws.description, ws.IP_address, ws.creation_date
                    FROM workstation ws
                    INNER JOIN workstation_group wsg ON ws.workstation_group=wsg.id
                    INNER JOIN LOCALISABLE loc ON wsg.name = loc.id
                    WHERE ws.name LIKE :name
                """, {'name': workstation_name})
                workstation = cursor.fetchone()

            if workstation:
                if new_group:
                    # If the user has selected a new group, perform the update
                    with connections[db_alias].cursor() as cursor:
                        cursor.execute("""
                            UPDATE workstation 
                            SET WORKSTATION_GROUP = :group_id 
                            WHERE name = :name
                        """, {'group_id': new_group.wsg_id, 'name': workstation_name})
                        response_data['status'] = 'success'
                        response_data['message'] = 'Workstation group updated successfully!'
                    return JsonResponse(response_data)
                else:
                    # Render the form with workstation details if only search is performed
                    return render(request, 'move_workstation.html', {
                        'form': form,
                        'workstation': workstation
                    })
            else:
                response_data['status'] = 'error'
                response_data['message'] = 'Workstation not found.'
                return JsonResponse(response_data)
        else:
            print("Form errors:", form.errors)  # Debugging output
            response_data['status'] = 'error'
            response_data['message'] = 'Form validation failed.'
            return JsonResponse(response_data)

    else:
        form = WorkstationForm()

    return render(request, 'move_workstation.html', {'form': form, 'workstation': workstation})

