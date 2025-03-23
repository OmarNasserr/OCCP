# Generated by Django 5.1.7 on 2025-03-22 20:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Charger',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('charge_point_id', models.CharField(max_length=100, unique=True)),
                ('charge_point_model', models.CharField(max_length=100)),
                ('charge_point_vendor', models.CharField(max_length=100)),
                ('status', models.CharField(default='Connected', max_length=50)),
                ('connected_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='StatusLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(max_length=50)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('charger', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='status_logs', to='chargers.charger')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_tag', models.CharField(max_length=100)),
                ('connector_id', models.IntegerField()),
                ('meter_start', models.IntegerField()),
                ('meter_stop', models.IntegerField(blank=True, null=True)),
                ('start_time', models.DateTimeField(auto_now_add=True)),
                ('stop_time', models.DateTimeField(blank=True, null=True)),
                ('charger', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='chargers.charger')),
            ],
        ),
    ]
