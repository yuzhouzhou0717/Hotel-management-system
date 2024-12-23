# Generated by Django 5.1.3 on 2024-11-27 08:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotel', '0017_table_check_out_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='finance',
            name='finance_type',
            field=models.CharField(blank=True, choices=[('housing', '住房'), ('meal', '就餐')], max_length=10, null=True),
        ),
    ]
