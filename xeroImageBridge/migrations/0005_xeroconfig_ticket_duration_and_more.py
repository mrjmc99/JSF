# Generated by Django 4.2.5 on 2024-09-06 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xeroImageBridge', '0004_xeroconfig_display_vars_xeroconfig_query_constraints'),
    ]

    operations = [
        migrations.AddField(
            model_name='xeroconfig',
            name='ticket_duration',
            field=models.IntegerField(default=1800),
        ),
        migrations.AlterField(
            model_name='xeroconfig',
            name='display_vars',
            field=models.CharField(default='theme=ahsxero&PatientID={patient_id}&AccessionNumber={accession_number}', max_length=255),
        ),
        migrations.AlterField(
            model_name='xeroconfig',
            name='query_constraints',
            field=models.CharField(default='PatientID={patient_id}', max_length=255),
        ),
        migrations.AlterField(
            model_name='xeroconfig',
            name='xero_domain',
            field=models.CharField(default='agility', max_length=255),
        ),
    ]
