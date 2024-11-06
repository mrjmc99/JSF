from django.db import models
from timezone_updater.models import EISystem
class Facility(models.Model):
    name = models.CharField(max_length=255)
    facility_id = models.IntegerField()
    ei_system = models.ForeignKey(EISystem, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} (ID: {self.facility_id})"

class FacilityGroup(models.Model):
    ei_system = models.ForeignKey('timezone_updater.EISystem', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    facilities = models.ManyToManyField(Facility)

    def __str__(self):
        return self.name

class AppPermissions(models.Model):
    class Meta:
        permissions = [
            ("use_updatecontact", "Can use Contact Updater"),
        ]