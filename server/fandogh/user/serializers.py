from django.db import models
from rest_framework import serializers
from rest_framework.serializers import Serializer

from user.models import EarlyAccessRequest


class UserSerializer(Serializer):
    email = serializers.EmailField()
    password = models.CharField(max_length=128)

    class Meta:
        exclude = ('password',)


class EarlyAccessRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = EarlyAccessRequest
        fields = ('email',)
