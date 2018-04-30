from rest_framework.serializers import ModelSerializer

from image.models import Build
from .models import WebApp, AppVersion


class AppSerializer(ModelSerializer):
    class Meta:
        model = WebApp
        fields = ('name',)


class AppVersionSerializer(ModelSerializer):
    class Meta:
        model = AppVersion
        fields = ('version', 'state')


class BuildSerializer(ModelSerializer):
    class Meta:
        model = Build
        fields = ('logs', 'start_date', 'end_date')
