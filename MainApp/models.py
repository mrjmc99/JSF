from django.db import models

class AppLink(models.Model):
    name = models.CharField(max_length=255, unique=True)
    url = models.CharField(max_length=255)  # Changed from URLField to CharField
    description = models.TextField(blank=True, null=True)
    visible = models.BooleanField(default=True)
    required_permission = models.CharField(max_length=255, help_text="Permission required to access this app.")

    def __str__(self):
        return self.name

class AppPermissions(models.Model):
    class Meta:
        #abstract = True  # This ensures the model doesn't create a table
        permissions = [
            ("use_JSF", "Can use JSF"),
        ]