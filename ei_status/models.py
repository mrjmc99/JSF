from django.db import models

# Create your models here.
class AppPermissions(models.Model):
    class Meta:
        #abstract = True  # This ensures the model doesn't create a table
        permissions = [
            ("use_ei_status", "Can use EI Cluster Status"),
        ]