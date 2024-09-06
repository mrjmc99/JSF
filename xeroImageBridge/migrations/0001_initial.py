# Generated by Django 4.2.5 on 2024-09-06 16:57

from django.db import migrations, models


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
                'permissions': [('use_xeroImageBridge', 'Can use Xero Image Bridge')],
            },
        ),
    ]
