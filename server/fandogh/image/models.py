from django.db import models

from webapp.models import AppVersion
import uuid


class Build(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    logs = models.TextField()
    version = models.ForeignKey(AppVersion, on_delete=models.DO_NOTHING, related_name='builds')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(auto_now=True)