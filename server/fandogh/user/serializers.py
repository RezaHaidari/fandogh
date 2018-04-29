from django.db import models
from rest_framework import serializers
from rest_framework.serializers import Serializer


class UserSerializer(Serializer):
    email = serializers.EmailField()
    password = models.CharField(max_length=128)

    class Meta:
        exclude = ('password',)
