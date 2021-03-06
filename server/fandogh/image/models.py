from django.contrib.auth.models import User
from django.db import models
import uuid


class Image(models.Model):
    name = models.CharField(primary_key=True, max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, related_name='images', on_delete=models.CASCADE)


class ImageVersion(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='versions')
    version = models.CharField(max_length=30)
    deleted = models.BooleanField(default=False)
    source = models.FileField()
    state = models.CharField(max_length=60, default='PENDING')  # PENDING, BUILDING, BUILD_FAILED, BUILT


class ImageBuild(models.Model):
    class Meta:
        ordering = ('-start_date',)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    logs = models.TextField()
    version = models.ForeignKey(ImageVersion, on_delete=models.DO_NOTHING, related_name='builds')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(auto_now=True)

