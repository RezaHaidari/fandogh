import random
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class EarlyAccessRequest(models.Model):
    email = models.EmailField(unique=True)


class Namespace(models.Model):
    name = models.CharField(max_length=200, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.OneToOneField(to=User, related_name='namespace', on_delete=models.CASCADE)


DEFAULT_NAMESPACE = Namespace(name='default')


def _get_code():
    return str(random.randint(10000000, 99999999))


class ConfirmKey(models.Model):
    class Meta:
        abstract = True

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    code = models.CharField(max_length=8, default=_get_code)
    used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def _get_confirm_code(cls, user_id, code):
        last_valid_date = datetime.now() - timedelta(days=1)
        return cls.objects.filter(
            used=False,
            created_at__gt=last_valid_date,
            code=code,
            user_id=user_id,
        ).first()


class ActivationCode(ConfirmKey):
    @classmethod
    def activate_user(cls, user_id, code):
        activation_code = cls._get_confirm_code(user_id, code)
        if activation_code is None:
            raise ActivationCode.DoesNotExist()
        activation_code.used = True
        activation_code.save()
        User.objects.filter(id=user_id).update(is_active=True)


class RecoveryToken(ConfirmKey):
    @classmethod
    def validate(cls, user_id, code):
        recovery_token = cls._get_confirm_code(user_id, code)
        if recovery_token is None:
            raise RecoveryToken.DoesNotExist
        recovery_token.used = True
        recovery_token.save()
