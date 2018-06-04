from rest_framework import serializers

from user.models import DEFAULT_NAMESPACE


class ServiceSerializer(serializers.Serializer):
    image_name = serializers.CharField(max_length=100)
    image_version = serializers.CharField(max_length=100)
    service_name = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True)
    environment_variables = serializers.DictField()
    port = serializers.IntegerField(default=80)


class ServiceResponseSerializer(serializers.Serializer):
    url = serializers.SerializerMethodField()
    name = serializers.CharField()
    start_date = serializers.CharField()
    state = serializers.CharField()

    def get_url(self, ctx):
        namespace = ctx.get('namespace', DEFAULT_NAMESPACE)
        name = ctx.get('name')
        if namespace.name == 'default':
            return 'http://%s.fandogh.cloud' % name
        else:
            return 'http://%s.%s.fandogh.cloud' % (name, namespace.name)
