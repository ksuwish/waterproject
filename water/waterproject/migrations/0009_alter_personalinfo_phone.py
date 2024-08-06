# Generated by Django 5.0.7 on 2024-08-06 11:05

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('waterproject', '0008_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personalinfo',
            name='phone',
            field=models.CharField(blank=True, max_length=11, validators=[django.core.validators.RegexValidator(code='invalid_phone', regex='^05\\d{10}$')]),
        ),
    ]
