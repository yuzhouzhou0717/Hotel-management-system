# Generated by Django 5.1.3 on 2024-11-28 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotel', '0021_table_seat_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='table',
            name='seat_type',
            field=models.CharField(choices=[('hall', 'Hall'), ('box', 'Box')], max_length=10),
        ),
    ]
