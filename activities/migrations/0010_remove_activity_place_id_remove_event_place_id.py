# Generated by Django 5.2.1 on 2025-06-22 13:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0009_event_place_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activity',
            name='place_id',
        ),
        migrations.RemoveField(
            model_name='event',
            name='place_id',
        ),
    ]
