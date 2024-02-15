# sites/models.py
from django.db import models

# Create your models here.
class AppPermissions(models.Model):
    class Meta:
        #abstract = True  # This ensures the model doesn't create a table
        permissions = [
            ("use_sites", "Can use sites"),
        ]


class SiteURL(models.Model):
    url = models.URLField()
    description = models.TextField()

    def __str__(self):
        return self.description
