from rest_framework import serializers

from image.models import *
from .models import WebApp, AppVersion


class AppSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebApp
        fields = ('name',)


class AppVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppVersion
        fields = ('version', 'state')


class BuildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Build
        fields = ('logs', 'start_date', 'end_date')


class ServiceSerializer(serializers.Serializer):
    img_version = serializers.CharField(max_length=100)
    app_name = serializers.CharField(max_length=100)
    service_name = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True)


class CreatedServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ('name', 'start_date', 'state')


class ContainerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ('container_id',)
