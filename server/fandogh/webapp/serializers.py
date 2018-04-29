from rest_framework.serializers import ModelSerializer

from .models import WebApp, AppVersion


class AppSerializer(ModelSerializer):
    class Meta:
        model = WebApp
        fields = ('name',)


class AppVersionSerializer(ModelSerializer):
    class Meta:
        model = AppVersion
        fields = ('version',)
