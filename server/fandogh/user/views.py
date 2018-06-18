import logging

from django.contrib.auth.hashers import make_password
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.db.transaction import atomic
from django.http import QueryDict
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.views import ObtainJSONWebToken

from common.response import ErrorResponse, GeneralResponse, ErrorListResponse
from user.models import Namespace
from .serializers import UserSerializer, EarlyAccessRequestSerializer
from common.response import ErrorResponse, GeneralResponse
from user.models import Namespace, ActivationCode, RecoveryToken
from user.services import send_confirmation_email, send_recovery_token
from .serializers import UserSerializer, EarlyAccessRequestSerializer, IdentitySerializer, EmailSerializer, \
    RecoverySerializer

error_logger = logging.getLogger("error")


class TokenView(ObtainJSONWebToken):
    def post(self, request):
        username = request.data.get("username", None)
        if username:
            if type(request.data) == QueryDict:
                request.data._mutable = True
            # request.data["username"] = normalize_email(username)
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            token = serializer.object.get('token')
            response_data = {
                "token": token
            }

            return Response(response_data)

        return GeneralResponse(_("Username or password is wrong"), status=status.HTTP_400_BAD_REQUEST)


class EarlyAccessView(APIView):
    def post(self, request):
        serialized = EarlyAccessRequestSerializer(data=request.data)
        if serialized.is_valid():
            try:
                serialized.save()
                return GeneralResponse(_("Your early access request registered successfully."))
            except Exception as e:
                error_logger.error("Error in early access registration. {}".format(e))
                error_logger.error("Error occurred in saving  early access request. email is: {}".format(serialized.validated_data['email']))
                return ErrorResponse(serialized.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return ErrorResponse(serialized.errors, status=status.HTTP_400_BAD_REQUEST)


class AccountView(APIView):
    def post(self, request):
        serialized = UserSerializer(data=request.data)
        if serialized.is_valid():
            try:
                with atomic():
                    u = User.objects.create_user(
                        email=serialized.validated_data['email'],
                        username=serialized.validated_data['email'],
                        password=serialized.initial_data['password'],
                        first_name='',
                        last_name='',
                        is_active=False,
                    )
                    if u:
                        Namespace.objects.create(name=serialized.validated_data['namespace'], owner=u)
                        send_confirmation_email(u)
                        return GeneralResponse(_("User has been registered successfully"), status=status.HTTP_201_CREATED)
            except Exception as e:
                error_logger.error("Error in creating account. {}".format(e))
                return GeneralResponse(
                    _("A user with current email or namespace exists"), status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return ErrorListResponse(serialized.errors)


class ActivationView(APIView):
    def patch(self, request, activation_code):
        serializer = IdentitySerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            ActivationCode.activate_user(
                code=activation_code,
                user_id=serializer.validated_data['id']
            )
            return GeneralResponse(_("Your account has been activated"))
        except ActivationCode.DoesNotExist:
            return GeneralResponse(_("Requested code does not exist"), status=404)
        except ValidationError:
            return GeneralResponse(_("Invalid request"), status=400)


class OnetimeTokenView(APIView):
    def post(self, request):
        serializer = EmailSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            send_recovery_token(serializer.validated_data['user'])
            return GeneralResponse(_("An email containing account recovery instruction has been sent to you."))
        except ValidationError:
            return ErrorResponse(serializer.errors, status=400)

    def patch(self, request, recovery_token):
        serializer = RecoverySerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            RecoveryToken.validate(
                code=recovery_token,
                user_id=serializer.validated_data['id']
            )
            User.objects.filter(id=serializer.validated_data['id']).update(
                password=make_password(serializer.validated_data['new_password'])
            )
            return GeneralResponse(_("Your account has been activated"))
        except RecoveryToken.DoesNotExist:
            return GeneralResponse(_("Requested code does not exist"), status=404)
        except ValidationError:
            return GeneralResponse(_("Invalid request"), status=400)
