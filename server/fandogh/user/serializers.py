from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import Serializer

from user.models import EarlyAccessRequest


class UserSerializer(Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128)
    namespace = serializers.CharField(max_length=20)

    class Meta:
        exclude = ('password',)


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
            raise ValidationError("User doesn't exists")
        return attrs


class RecoverySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    new_password = serializers.CharField()
