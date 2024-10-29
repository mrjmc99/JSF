# updatecontact/management/commands/update_facilities.py
from django.core.management.base import BaseCommand
from updatecontact.models import Facility
import requests


class Command(BaseCommand):
    help = 'Update facilities list from external API'

    def handle(self, *args, **kwargs):
        response = requests.get('https://mivcsptest2.adventhealth.com/ris/web/v1/contactusers/facilities')
        facilities_data = response.json()

        for facility in facilities_data:
            Facility.objects.update_or_create(
                id=facility['id'],
                defaults={'name': facility['name']}
            )

        self.stdout.write(self.style.SUCCESS('Facilities list updated successfully.'))
