# Generated by Django 4.2.5 on 2025-01-20 19:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('timezone_updater', '0004_apppermissions'),
        ('updatecontact', '0003_apppermissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='EIUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('login_name', models.CharField(max_length=100)),
                ('profession_id', models.IntegerField()),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('ei_system', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timezone_updater.eisystem')),
            ],
            options={
                'unique_together': {('ei_system', 'login_name', 'profession_id')},
            },
        ),
        migrations.CreateModel(
            name='EIUserFacilityAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_synced', models.DateTimeField(auto_now=True)),
                ('facility', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='updatecontact.facility')),
                ('facility_group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='updatecontact.facilitygroup')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='updatecontact.eiuser')),
            ],
            options={
                'unique_together': {('user', 'facility')},
            },
        ),
    ]
