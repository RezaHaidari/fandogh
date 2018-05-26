from rest_framework import serializers

from service.models import Service
from user.models import DEFAULT_NAMESPACE


class ServiceSerializer(serializers.Serializer):
    image_name = serializers.CharField(max_length=100)
    image_version = serializers.CharField(max_length=100)
    service_name = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True)
    environment_variables = serializers.DictField()
    port = serializers.IntegerField(default=80)


class CreatedServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ('name', 'start_date', 'state')


class ContainerSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        namespace = getattr(obj.owner, 'nemspace', DEFAULT_NAMESPACE)
        if namespace.name == 'default':
            return 'http://%s.fandogh.cloud' % (obj.name)
        else:
            return 'http://%s.%s.fandogh.cloud' % (obj.name, namespace.name)

    class Meta:
        model = Service
        fields = ('container_id', 'url',)
