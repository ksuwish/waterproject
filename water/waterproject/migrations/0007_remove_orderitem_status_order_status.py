# Generated by Django 5.0.7 on 2024-08-06 08:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('waterproject', '0006_orderitem_status_alter_personalinfo_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderitem',
            name='status',
        ),
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('completed', 'Completed'), ('pending', 'Pending')], default=1, max_length=10),
            preserve_default=False,
        ),
    ]
