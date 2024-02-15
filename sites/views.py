# sites/views.py
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required,permission_required
from .models import SiteURL

@permission_required('sites.use_sites')
def index(request):
    sites_list = SiteURL.objects.all()
    return render(request, 'sites.html', {'sites_list': sites_list})
