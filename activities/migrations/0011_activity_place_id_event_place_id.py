# Generated by Django 5.2.1 on 2025-06-22 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0010_remove_activity_place_id_remove_event_place_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='place_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='place_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
