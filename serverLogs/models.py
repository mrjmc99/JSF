# serverlogs/models.py
from django.db import models
from fernet_fields import EncryptedCharField
# Create your models here.
class AppPermissions(models.Model):
    class Meta:
        #abstract = True  # This ensures the model doesn't create a table
        permissions = [
            ("use_serverLogs", "Can use Server Logs"),
        ]

class PACSCore(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class RemoteWindowsServer(models.Model):
    core = models.ForeignKey(PACSCore, on_delete=models.CASCADE, related_name="servers")
    name = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    credentials = EncryptedCharField(max_length=500)
    logs_folder = models.CharField(max_length=500)

    class Meta:
        unique_together = ['core', 'name']

    def __str__(self):
        return f"{self.name} ({self.core.name})"

class PredefinedSearch(models.Model):
    name = models.CharField(max_length=200)
    search_query = models.TextField()

    def __str__(self):
        return self.name
