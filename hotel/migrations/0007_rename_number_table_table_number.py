# Generated by Django 5.1.3 on 2024-11-13 13:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hotel', '0006_alter_table_check_in_time'),
    ]

    operations = [
        migrations.RenameField(
            model_name='table',
            old_name='number',
            new_name='table_number',
        ),
    ]
