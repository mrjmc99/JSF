# MoveEIWorkstation/views.py
from django.shortcuts import render
from django.db import connections
from .forms import WorkstationForm
from django.contrib import messages

def move_workstation(request):
    workstation = None
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
                           ws.name as workstation, ws.description, ws.IP_address
                    FROM workstation ws
                    INNER JOIN workstation_group wsg ON ws.workstation_group=wsg.id
                    INNER JOIN LOCALISABLE loc ON wsg.name = loc.id
                    WHERE ws.name LIKE :name
                """, {'name': workstation_name})
                workstation = cursor.fetchone()

            if not workstation:
                messages.error(request, 'Workstation not found.')
            elif new_group:
                # If the user has selected a new group, perform the update
                with connections[db_alias].cursor() as cursor:
                    cursor.execute("""
                        UPDATE workstation 
                        SET WORKSTATION_GROUP = :group_id 
                        WHERE name = :name
                    """, {'group_id': new_group.wsg_id, 'name': workstation_name})
                    messages.success(request, 'Workstation group updated successfully!')
            else:
                # If no new group is selected, show the current workstation information
                messages.info(request, 'Workstation found. You can now update its group.')

    else:
        form = WorkstationForm()

    return render(request, 'move_workstation.html', {'form': form, 'workstation': workstation})
