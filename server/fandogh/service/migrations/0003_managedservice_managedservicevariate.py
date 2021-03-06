# Generated by Django 2.0.4 on 2018-06-18 11:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('service', '0002_auto_20180604_1712'),
    ]

    operations = [
        migrations.CreateModel(
            name='ManagedService',
            fields=[
                ('name', models.CharField(max_length=100, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='ManagedServiceVariate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('required_config', models.CharField(max_length=4000)),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variates', to='service.ManagedService')),
            ],
        ),
    ]
