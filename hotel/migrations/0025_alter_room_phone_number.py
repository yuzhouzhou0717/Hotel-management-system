# Generated by Django 5.1.3 on 2024-11-30 03:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotel', '0024_room_phone_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='phone_number',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
