# mainapp/views.py
from django.shortcuts import render
from .models import AppLink
from django.contrib.auth.decorators import login_required,permission_required
from django.contrib import messages

@login_required
def landing_page(request):
    # Fetch all visible AppLinks
    app_links = AppLink.objects.filter(visible=True)

    # Filter app_links by checking if the user has the required permission for each link
    app_links = [app_link for app_link in app_links if request.user.has_perm(app_link.required_permission)]

    # If no app links available for the user, set a message
    if not app_links:
        messages.warning(request, 'You do not have permission to access any apps. Please contact your System Administrator.')

    context = {
        'app_links': app_links,
        'is_home_page': True,
    }
    return render(request, 'landing_page.html', context)
