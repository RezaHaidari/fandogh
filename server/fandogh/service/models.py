import uuid

from django.contrib.auth.models import User
from django.db import models


class Service(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='services')
    container_id = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    start_date = models.DateTimeField(auto_now_add=True)
    state = models.CharField(max_length=100)
