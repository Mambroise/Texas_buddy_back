# Generated by Django 5.2.1 on 2025-06-26 14:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0012_activity_ad_priority_activity_is_unique_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activity',
            name='ad_priority',
        ),
        migrations.RemoveField(
            model_name='event',
            name='ad_priority',
        ),
    ]
