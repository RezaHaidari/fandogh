from django.db import models

from webapp.models import AppVersion


class Build(models.Model):
    logs = models.TextField()
    version = models.ForeignKey(AppVersion, on_delete=models.DO_NOTHING, related_name='builds')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(auto_now=True)
