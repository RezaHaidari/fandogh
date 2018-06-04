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


class ServiceResponseSerializer(serializers.Serializer):
    url = serializers.SerializerMethodField()

    def get_url(self, ctx):
        namespace = ctx.get('namespace', DEFAULT_NAMESPACE)
        service_name = ctx.get('service_name')
        if namespace.name == 'default':
            return 'http://%s.fandogh.cloud' % service_name
        else:
            return 'http://%s.%s.fandogh.cloud' % (service_name, namespace.name)
