# Generated by Django 5.2.1 on 2025-06-27 22:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0003_alter_priorityad_advertisement'),
    ]

    operations = [
        migrations.AlterField(
            model_name='priorityad',
            name='advertisement',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='priority_entries', to='ads.advertisement'),
        ),
    ]
