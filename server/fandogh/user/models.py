from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class EarlyAccessRequest(models.Model):
    email = models.EmailField(unique=True)


class Namespace(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.OneToOneField(to=User, related_name='namespace', on_delete=models.CASCADE)


DEFAULT_NAMESPACE = Namespace(name='default')
