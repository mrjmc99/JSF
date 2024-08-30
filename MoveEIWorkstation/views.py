from django.http import JsonResponse
from django.shortcuts import render
from django.db import connections
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from .forms import WorkstationForm


@permission_required('MoveEIWorkstation.use_move_ei_workstations')
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
                           ws.name as workstation, ws.description, ws.IP_address, ws.creation_date
                    FROM workstation ws
                    INNER JOIN workstation_group wsg ON ws.workstation_group=wsg.id
                    INNER JOIN LOCALISABLE loc ON wsg.name = loc.id
                    WHERE UPPER(ws.name) = UPPER(:name)
                """, {'name': workstation_name})
                workstation = cursor.fetchone()

            if workstation:
                if 'new_group' in request.POST:
                    # If the user has selected a new group, perform the update
                    with connections[db_alias].cursor() as cursor:
                        cursor.execute("""
                            UPDATE workstation 
                            SET WORKSTATION_GROUP = :group_id 
                            WHERE UPPER(name) = UPPER(:name)
                        """, {'group_id': new_group.wsg_id, 'name': workstation_name})
                        messages.success(request, 'Workstation group updated successfully!')
                        # After processing the form, clear the messages
                        storage = messages.get_messages(request)
                        list(storage)  # This iteration is necessary to clear the messages
                        return JsonResponse({'status': 'success', 'message': 'Workstation group updated successfully!'})
                else:
                    # After processing the form, clear the messages
                    storage = messages.get_messages(request)
                    list(storage)  # This iteration is necessary to clear the messages
                    # Render the form with workstation details if only search is performed
                    return render(request, 'move_workstation.html', {
                        'form': form,
                        'workstation': workstation
                    })
            else:
                messages.error(request, 'Workstation not found.')
                # After processing the form, clear the messages
                storage = messages.get_messages(request)
                list(storage)  # This iteration is necessary to clear the messages
                return render(request, 'move_workstation.html', {'form': form})

        else:
            messages.error(request, 'Form validation failed.')
            # After processing the form, clear the messages
            storage = messages.get_messages(request)
            list(storage)  # This iteration is necessary to clear the messages
            return render(request, 'move_workstation.html', {'form': form})

    else:
        form = WorkstationForm()
        # After processing the form, clear the messages
    storage = messages.get_messages(request)
    list(storage)  # This iteration is necessary to clear the messages
    return render(request, 'move_workstation.html', {'form': form, 'workstation': workstation})