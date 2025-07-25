# Generated by Django 5.2.1 on 2025-07-02 12:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0010_remove_adinvoice_partner_adinvoice_advertisement_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adinvoice',
            name='advertisement',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoices', to='ads.advertisement'),
        ),
        migrations.AlterField(
            model_name='adinvoice',
            name='due_date',
            field=models.DateField(),
        ),
    ]
