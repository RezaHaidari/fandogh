from django.contrib.auth.models import User
from django.db import models


class WebApp(models.Model):
    name = models.CharField(primary_key=True, max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, related_name='apps', on_delete=models.CASCADE)


class AppVersion(models.Model):
    app = models.ForeignKey(WebApp, on_delete=models.CASCADE, related_name='versions')
    version = models.CharField(max_length=30)
    deleted = models.BooleanField(default=False)
    source = models.FileField()
    state = models.CharField(max_length=60, default='PENDING')  # PENDING, BUILDING, BUILD_FAILED, BUILT
