from rest_framework import serializers

from service.models import Service


class ServiceSerializer(serializers.Serializer):
    img_version = serializers.CharField(max_length=100)
    app_name = serializers.CharField(max_length=100)
    service_name = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True)
    environment_variables = serializers.DictField()


class CreatedServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ('name', 'start_date', 'state')


class ContainerSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return 'http://%s.fandogh.cloud' % obj.name

    class Meta:
        model = Service
        fields = ('container_id', 'url',)
