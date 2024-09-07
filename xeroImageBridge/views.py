from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .utils import get_xero_ticket
from .models import XeroConfig
from django.utils.text import slugify

@permission_required('xeroImageBridge.use_xeroImageBridge')
def xero_imaging_bridge(request, xero_server_slug=None):
    xero_servers = XeroConfig.objects.all()

    if xero_server_slug:
        xero_config = get_object_or_404(XeroConfig, xero_server_slug=slugify(xero_server_slug))
    else:
        # If no slug is provided, show the server selection page
        return render(request, 'xero_server_selection.html', {'xero_servers': xero_servers})

    if request.method in ['POST', 'GET']:
        accession_number = request.POST.get('accession_number') if request.method == 'POST' else request.GET.get('accession_number')
        patient_id = request.POST.get('patient_id') if request.method == 'POST' else request.GET.get('patient_id')

        if not patient_id:
            return render(request, 'xero_imaging_bridge_form.html', {
                'xero_servers': xero_servers,
                'error_message': "All fields are required."
            })

        query_constraints = xero_config.query_constraints.format(patient_id=patient_id, accession_number=accession_number)
        accession_number = accession_number or ""

        display_vars = xero_config.display_vars.format(patient_id=patient_id, accession_number=accession_number)
        if not accession_number:
            display_vars = display_vars.replace("&AccessionNumber=", "")

        xero_ticket = get_xero_ticket(
            request.user.username,
            xero_config.xero_user,
            xero_config.ticket_duration,
            xero_config.xero_password,
            xero_config.xero_server,
            xero_config.xero_domain,
            query_constraints,
            display_vars
        )

        if xero_ticket:
            return launch_xero_redirect(request, xero_config.xero_server, xero_ticket)
        else:
            return HttpResponse("Failed to generate Xero ticket", status=500)
    else:
        return HttpResponse("Method not allowed", status=405)

    return render(request, 'xero_imaging_bridge_form.html', {'xero_servers': xero_servers})
@permission_required('xeroImageBridge.use_xeroImageBridge')
def launch_xero_redirect(request, xero_server, xero_ticket):
    xero_url = f"https://{xero_server}/?ticket={xero_ticket}"
    return render(request, 'xero_redirect.html', {'xero_url': xero_url})
