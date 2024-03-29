# Generated by Django 4.2.5 on 2023-10-03 20:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AppPermissions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'permissions': [('use_serverLogs', 'Can use Server Logs')],
            },
        ),
        migrations.CreateModel(
            name='PACSCore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RemoteWindowsServer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('ip_address', models.GenericIPAddressField()),
                ('credentials', models.CharField(max_length=500)),
                ('logs_folder', models.CharField(max_length=500)),
                ('core', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='servers', to='serverLogs.pacscore')),
            ],
            options={
                'unique_together': {('core', 'name')},
            },
        ),
    ]
