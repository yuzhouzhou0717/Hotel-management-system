# Generated by Django 5.1.3 on 2024-11-30 04:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotel', '0025_alter_room_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='finance',
            name='additional_service_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='finance',
            name='total_amount',
            field=models.DecimalField(decimal_places=2, default=0, editable=False, max_digits=10),
        ),
    ]