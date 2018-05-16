from rest_framework import serializers

from image.models import *


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('name', 'created_at', 'owner')


class ImageVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageVersion
        fields = ('version', 'state')


class ImmageBuildSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageBuild
        fields = ('logs', 'start_date', 'end_date', 'state')

    state = serializers.SerializerMethodField()

    def get_state(self, obj):
        return obj.version.state
