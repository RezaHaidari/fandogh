from django.contrib.auth.models import User
from django.db import models
import uuid


class ManagedService(models.Model):
    name = models.CharField(primary_key=True, max_length=100)


class ManagedServiceVariate(models.Model):
    service = models.ForeignKey(to=ManagedService, related_name="variates", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    required_config = models.CharField(max_length=4000)
