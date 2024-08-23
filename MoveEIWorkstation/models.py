# MoveEIWorkstation/models.py
from django.db import models

class WorkstationGroup(models.Model):
    wsg_id = models.IntegerField(unique=True)  # Store the workstation group ID from Oracle
    name = models.CharField(max_length=100)    # Friendly name

    def __str__(self):
        return self.name

class AppPermissions(models.Model):
    class Meta:
        #abstract = True  # This ensures the model doesn't create a table
        permissions = [
            ("use_move_ei_workstations", "Can use Move EI Workstations"),
        ]