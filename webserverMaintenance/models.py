# webservermaintenance/models.py
from django.db import models
from django.contrib.auth.models import User

class AppPermissions(models.Model):
    class Meta:
        #abstract = True  # This ensures the model doesn't create a table
        permissions = [
            ("use_webserverMaintenance", "Can use Webserver Maintenance"),
        ]

class CommandLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    command = models.CharField(max_length=200)
    result = models.TextField()

    def __str__(self):
        return f"{self.user} executed {self.command} at {self.timestamp}"

class RemoteServer(models.Model):
    name = models.CharField(max_length=255, unique=True)  # The actual name
    friendly_name = models.CharField(max_length=255)  # The display name
    hostname = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    private_key_path = models.CharField(max_length=512)

    def __str__(self):
        return self.name

class RemoteCommand(models.Model):
    name = models.CharField(max_length=255, unique=True)  # A friendly name for the command
    command = models.TextField()

    def __str__(self):
        return self.name