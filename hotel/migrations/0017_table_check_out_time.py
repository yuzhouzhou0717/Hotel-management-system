# Generated by Django 5.1.3 on 2024-11-27 05:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotel', '0016_finance'),
    ]

    operations = [
        migrations.AddField(
            model_name='table',
            name='check_out_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
