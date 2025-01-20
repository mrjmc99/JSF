# updatecontact/models.py
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
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class EIUser(models.Model):
    ei_system = models.ForeignKey(EISystem, on_delete=models.CASCADE)
    login_name = models.CharField(max_length=100)
    profession_id = models.IntegerField()
    last_updated = models.DateTimeField(auto_now=True)
    facility_groups = models.ManyToManyField('FacilityGroup', blank=True)
    class Meta:
        unique_together = ('ei_system', 'login_name', 'profession_id')

    def __str__(self):
        return f"{self.login_name} ({self.ei_system.name})"

class EIUserFacilityAssignment(models.Model):
    user = models.ForeignKey(EIUser, on_delete=models.CASCADE, related_name="assignments")
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    facility_group = models.ForeignKey(FacilityGroup, null=True, blank=True, on_delete=models.SET_NULL)
    last_synced = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'facility')

    def __str__(self):
        return f"{self.user.login_name} - {self.facility.name}"

class AppPermissions(models.Model):
    class Meta:
        permissions = [
            ("use_updatecontact", "Can use Contact Updater"),
        ]