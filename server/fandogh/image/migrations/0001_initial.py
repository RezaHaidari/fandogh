# Generated by Django 2.0.4 on 2018-05-16 18:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('name', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='apps', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ImageBuild',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('logs', models.TextField()),
                ('start_date', models.DateTimeField(auto_now_add=True)),
                ('end_date', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ('-start_date',),
            },
        ),
        migrations.CreateModel(
            name='ImageVersion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.CharField(max_length=30)),
                ('deleted', models.BooleanField(default=False)),
                ('source', models.FileField(upload_to='')),
                ('state', models.CharField(default='PENDING', max_length=60)),
                ('image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='versions', to='image.Image')),
            ],
        ),
        migrations.AddField(
            model_name='imagebuild',
            name='version',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='builds', to='image.ImageVersion'),
        ),
    ]
