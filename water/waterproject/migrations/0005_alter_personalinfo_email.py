# Generated by Django 5.0.7 on 2024-08-02 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('waterproject', '0004_alter_personalinfo_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personalinfo',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
    ]
