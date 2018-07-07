from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from service.managed_services.mysql import get_deployer
from service.utils import generate_ingress_url
from user.models import DEFAULT_NAMESPACE
from django.utils.translation import ugettext as _


class ServiceSerializer(serializers.Serializer):
    image_name = serializers.CharField(max_length=100)
    image_version = serializers.CharField(max_length=100)
    service_name = serializers.RegexField(max_length=100, required=True, allow_blank=False, allow_null=False,
                                          regex=r'^[a-z]+(-*[a-z0-9]+)*$', error_messages={
            "invalid": _("service name should consist of lowercase letters, digits or dash, "
                         "for example my-service2 is valid")
        })
    environment_variables = serializers.DictField()
    port = serializers.IntegerField(default=80)
    service_type = serializers.CharField(allow_blank=True, default='external')


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
        return generate_ingress_url(name, namespace.name)


class ManagedServiceSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    version = serializers.CharField(max_length=100)
    config = serializers.DictField()

    def validate(self, attrs):
        deployer = get_deployer(attrs['name'])
        if deployer is None:
            raise ValidationError({'name': [_('Requested service does not exists as a managed-service')]})
        configurable_options = deployer.get_configurable_options().keys()
        config_errors = []
        for user_config_key in attrs.get('config', {}):
            if user_config_key not in configurable_options:
                config_errors.append(
                    _("{} is not one of available config options for {}").format(user_config_key, attrs['name']))
        if len(config_errors) > 0:
            raise ValidationError({'config': config_errors})

        return attrs
