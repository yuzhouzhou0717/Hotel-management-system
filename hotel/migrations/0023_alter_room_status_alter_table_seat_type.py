# Generated by Django 5.1.3 on 2024-11-30 03:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotel', '0022_alter_table_seat_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='status',
            field=models.CharField(choices=[('vacant', '空房'), ('occupied', '已入住'), ('cleaning', '清洁中'), ('maintenance', '待维修')], default='vacant', max_length=100),
        ),
        migrations.AlterField(
            model_name='table',
            name='seat_type',
            field=models.CharField(choices=[('hall', '大厅'), ('box', '包厢')], max_length=10),
        ),
    ]
