# Generated by Django 5.1.3 on 2024-11-27 04:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotel', '0015_alter_room_id_card_alter_room_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Finance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('finance_type', models.CharField(choices=[('housing', '住房'), ('meal', '就餐')], max_length=10)),
                ('responsible_person', models.CharField(max_length=100)),
                ('details', models.TextField()),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
    ]