# timezone_updater/models.py

from django.db import models

class EISystem(models.Model):
    name = models.CharField(max_length=255)
    ei_fqdn = models.CharField(max_length=255)
    ei_user = models.CharField(max_length=255)
    ei_password = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class AppPermissions(models.Model):
    class Meta:
        #abstract = True  # This ensures the model doesn't create a table
        permissions = [
            ("use_timezone_updater", "Can use TimeZone Updater"),
        ]