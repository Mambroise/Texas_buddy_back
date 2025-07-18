# Generated by Django 5.2.1 on 2025-07-03 19:57

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('ein', models.CharField(blank=True, max_length=20, null=True)),
                ('siren', models.CharField(blank=True, max_length=20, null=True)),
                ('legal_structure', models.CharField(blank=True, max_length=30, null=True)),
                ('address', models.CharField(max_length=155)),
                ('tax_info', models.CharField(max_length=6)),
                ('tax_math', models.FloatField(blank=True, null=True)),
                ('email', models.CharField(max_length=150, unique=True)),
                ('phone', models.CharField(blank=True, max_length=15, null=True)),
                ('instagram', models.CharField(max_length=50)),
                ('is_in_texas', models.BooleanField(default=False)),
            ],
        ),
    ]
