from django.db import models
import json

class SavedQuery(models.Model):
    QUERY_TYPE_CHOICES = [
        ('impax', 'Impax'),
        ('ei', 'EI')
    ]

    name = models.CharField(max_length=200)
    query = models.TextField()
    _variables = models.TextField(default='[]')  # Internal representation
    query_type = models.CharField(max_length=5, choices=QUERY_TYPE_CHOICES, default='impax')  # New field for query type

    @property
    def variables(self):
        return json.loads(self._variables)

    @variables.setter
    def variables(self, value):
        self._variables = json.dumps(value)

    def __str__(self):
        return self.name

class FriendlyDBName(models.Model):
    db_alias = models.CharField(max_length=50, unique=True)
    friendly_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.friendly_name} ({self.db_alias})"

class AppPermissions(models.Model):
    class Meta:
        #abstract = True  # This ensures the model doesn't create a table
        permissions = [
            ("use_oracle_queries", "Can use Oracle Queries"),
        ]