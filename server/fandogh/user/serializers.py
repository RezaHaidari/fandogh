from django.contrib.auth.models import User
from django.db.models import Q
from django.db.transaction import atomic
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import Serializer

from user import models
from user.models import EarlyAccessRequest, Namespace
from django.utils.translation import ugettext as _


class UserSerializer(Serializer):
    username = serializers.RegexField(max_length=32, regex=r"^[a-zA-Z0-9\._]{3,32}$", error_messages={
        'invalid': _("Only lowercase english letters, digits, dash and dot are allowed in username")
    })
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128)
    namespace = serializers.CharField(max_length=20)

    class Meta:
        exclude = ('password',)

    def validate(self, attrs: dict):
        attrs['username'] = str(attrs['username']).lower()
        duplicate_user = models.User.objects.filter(Q(email=attrs['email']) | Q(username=attrs['username'])).first()
        if isinstance(duplicate_user, User):
            if duplicate_user.email == attrs['email']:
                raise ValidationError({'email': [_("Email address already exists")]})
            if duplicate_user.username == attrs['username']:
                raise ValidationError({'username': [_("Username already taken")]})
        if models.Namespace.objects.filter(name=attrs['namespace']).exists():
            raise ValidationError(
                {'namespace': [_("This name already used by another account, please choose another name")]}
            )
        return attrs

    def save(self, **kwargs):
        with atomic():
            u = User.objects.create_user(
                email=self.validated_data['email'],
                username=self.validated_data['username'],
                password=self.initial_data['password'],
                **kwargs
            )
            if u:
                Namespace.objects.create(name=self.validated_data['namespace'], owner=u)
            return u


class EarlyAccessRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = EarlyAccessRequest
        fields = ('email',)


class IdentitySerializer(serializers.Serializer):
    id = serializers.IntegerField()


class OTTRequestSerializer(serializers.Serializer):
    identifier = serializers.CharField()

    def validate(self, attrs):
        attrs = super(OTTRequestSerializer, self).validate(attrs)
        identifier = attrs['identifier'].split("+")[0]
        if '@' in identifier:
            user = User.objects.filter(email__startswith=identifier).first()
        else:
            user = User.objects.filter(username=identifier).first()
        if user is None:
            raise ValidationError({"identifier": [_("There is no user with this email/username")]})
        return {
            "user": user,
            **attrs
        }


class RecoverySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    new_password = serializers.CharField()
