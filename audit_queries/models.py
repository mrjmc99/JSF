from django.db import models
from oracleQuery.models import FriendlyDBName

class AuditQuery(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    query = models.TextField()
    variables = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    database = models.ForeignKey(FriendlyDBName, on_delete=models.CASCADE)
    multiple_queries = models.BooleanField(default=False)
    requires_preliminary = models.BooleanField(default=False)
    preliminary_query = models.TextField(blank=True, null=True, help_text="SQL query to fetch extra data needed for the main query")
    preliminary_db = models.ForeignKey(FriendlyDBName, on_delete=models.SET_NULL, blank=True, null=True, related_name="preliminary_queries", help_text="Database to run the preliminary query against")
    def __str__(self):
        return self.name

class SubQuery(models.Model):
    parent_query = models.ForeignKey(AuditQuery, related_name='sub_queries', on_delete=models.CASCADE)
    query = models.TextField()
    order = models.PositiveIntegerField()
    database = models.ForeignKey(FriendlyDBName, on_delete=models.CASCADE)

class AppPermissions(models.Model):
    class Meta:
        #abstract = True  # This ensures the model doesn't create a table
        permissions = [
            ("use_audit_queries", "Can use audit queries"),
        ]