# Generated by Django 4.2.5 on 2025-03-10 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('serverLogs', '0007_remove_remotelinuxserver_ssh_key_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='remotelinuxserver',
            name='logs_folder',
            field=models.CharField(default='/var/log/agfa/IMPAX_Agility/logging', max_length=500),
        ),
        migrations.AlterField(
            model_name='remotelinuxserver',
            name='ssh_username',
            field=models.CharField(default='agfaservice', max_length=100),
        ),
    ]
