# MoveEIWorkstation/forms.py
from django import forms
from .models import WorkstationGroup
from oracleQuery.models import FriendlyDBName

class WorkstationForm(forms.Form):
    db_alias = forms.ChoiceField(
        label='Database',
        choices=[(db.db_alias, db.friendly_name) for db in FriendlyDBName.objects.filter(db_alias__startswith='ei')]
    )
    workstation_name = forms.CharField(label='Workstation Name', max_length=100)
    new_group = forms.ModelChoiceField(queryset=WorkstationGroup.objects.all(), label='New Workstation Group', required=False)