# Generated by Django 4.2.5 on 2023-10-03 21:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('serverLogs', '0002_alter_remotewindowsserver_credentials'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='remotewindowsserver',
            name='credentials',
        ),
    ]
