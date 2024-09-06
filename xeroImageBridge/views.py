from django.contrib.auth.decorators import permission_required

secret_xero_server = 'server'
#secret_xero_server = 'adcvwebpaclx011.multihosp.net'
secret_jsf_user = 'jsf_user'  # Placeholder for JSF user
secret_xero_user = 'user'  # Placeholder for Xero user
secret_xero_password = 'password'
# xeroImageBridge/views.py
from django.shortcuts import render
from django.http import HttpResponse
from .utils import get_xero_ticket
from .models import XeroConfig
from django.utils.text import slugify

def xero_imaging_bridge(request, xero_server_slug=None):
    xero_servers = XeroConfig.objects.all()

    if xero_server_slug:
        xero_config = get_object_or_404(XeroConfig, xero_server_slug=slugify(xero_server_slug))
    else:
        # Handle the case when no server is specified:
        # Option 1: Redirect to a default or a listing page
        # Option 2: Show a selection page or an error message
        return render(request, 'xero_imaging_bridge_form.html', {
            'xero_servers': xero_servers,
            'error_message': 'Please select a Xero server.'
        })

    if request.method in ['POST', 'GET']:
        accession_number = request.POST.get('accession_number') if request.method == 'POST' else request.GET.get('accession_number')
        patient_id = request.POST.get('patient_id') if request.method == 'POST' else request.GET.get('patient_id')

        if not accession_number or not patient_id:
            return render(request, 'xero_imaging_bridge_form.html', {
                'xero_servers': xero_servers,
                'error_message': "All fields are required."
            })

        query_constraints = xero_config.query_constraints.format(patient_id=patient_id, accession_number=accession_number)
        display_vars = xero_config.display_vars.format(patient_id=patient_id, accession_number=accession_number)

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
