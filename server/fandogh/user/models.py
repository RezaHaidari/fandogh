from django.db import models


# Create your models here.
class EarlyAccessRequest(models.Model):
    email = models.EmailField(unique=True)
