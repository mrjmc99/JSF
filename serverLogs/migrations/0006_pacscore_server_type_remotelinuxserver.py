# Generated by Django 4.2.5 on 2025-03-10 14:47

from django.db import migrations, models
import django.db.models.deletion
import fernet_fields.fields


class Migration(migrations.Migration):

    dependencies = [
        ('serverLogs', '0005_predefinedsearch'),
    ]

    operations = [
        migrations.AddField(
            model_name='pacscore',
            name='server_type',
            field=models.CharField(choices=[('windows', 'Windows'), ('linux', 'Linux')], default='windows', help_text='Select the type of servers used by this PACS core.', max_length=10),
        ),
        migrations.CreateModel(
            name='RemoteLinuxServer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('ip_address', models.GenericIPAddressField()),
                ('ssh_username', models.CharField(max_length=100)),
                ('ssh_key', fernet_fields.fields.EncryptedCharField(max_length=2000)),
                ('logs_folder', models.CharField(max_length=500)),
                ('core', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='linux_servers', to='serverLogs.pacscore')),
            ],
            options={
                'unique_together': {('core', 'name')},
            },
        ),
    ]
