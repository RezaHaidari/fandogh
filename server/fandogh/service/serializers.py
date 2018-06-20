from rest_framework import serializers
from user.models import DEFAULT_NAMESPACE


class ServiceSerializer(serializers.Serializer):
    image_name = serializers.CharField(max_length=100)
    image_version = serializers.CharField(max_length=100)
    service_name = serializers.RegexField(max_length=100, required=True, allow_blank=False, allow_null=False,
                                          regex=r'^[a-z]+(-*[a-z0-9]+)*$', error_messages={
            "invalid": "service name should consist of lowercase letters, digits or dash, "
                       "for example my-service2 is valid"
        })
    environment_variables = serializers.DictField()
    port = serializers.IntegerField(default=80)
    service_type = serializers.CharField(allow_blank=True,default='external')


class ServiceResponseSerializer(serializers.Serializer):
    url = serializers.SerializerMethodField()
    name = serializers.CharField()
    start_date = serializers.CharField()
    state = serializers.CharField()
    service_type = serializers.CharField()

    def get_url(self, ctx):
        service_type = ctx.get('service_type', False)
        if service_type != 'external':
            return service_type
        namespace = ctx.get('namespace', DEFAULT_NAMESPACE)
        name = ctx.get('name')
        if namespace.name == 'default':
            return 'http://%s.fandogh.cloud' % name
        else:
            return 'http://%s.%s.fandogh.cloud' % (name, namespace.name)


class ManagedServiceSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    version = serializers.CharField(max_length=100)
    config = serializers.DictField()
