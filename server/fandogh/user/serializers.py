from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import Serializer

from user import models
from user.models import EarlyAccessRequest
from django.utils.translation import ugettext as _


class UserSerializer(Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128)
    namespace = serializers.CharField(max_length=20)

    class Meta:
        exclude = ('password',)

    def validate(self, attrs):
        if models.User.objects.filter(email=attrs['email']).exists():
            raise ValidationError({'email': [_("Email address already exists")]})
        if models.Namespace.objects.filter(name=attrs['namespace']).exists():
            raise ValidationError({'namespace': [_("This name already used by another account, please choose another name")]})
        return attrs


class EarlyAccessRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = EarlyAccessRequest
        fields = ('email',)


class IdentitySerializer(serializers.Serializer):
    id = serializers.IntegerField()


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        attrs = super(EmailSerializer, self).validate(attrs)
        try:
            attrs['user'] = User.objects.get(email=attrs['email'])
        except User.DoesNotExist:
            raise ValidationError(_("User doesn't exists"))
        return attrs


class RecoverySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    new_password = serializers.CharField()
