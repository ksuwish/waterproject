# Generated by Django 5.0.7 on 2024-08-07 09:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('waterproject', '0014_remove_address_postal_code_alter_address_country'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='postal_code',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Postal Code'),
        ),
    ]
