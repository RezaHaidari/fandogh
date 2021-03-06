import logging
from django.contrib.auth.hashers import make_password
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.views import ObtainJSONWebToken
from common.response import ErrorListResponse
from common.response import ErrorResponse, GeneralResponse
from user.models import ActivationCode, RecoveryToken, Namespace
from user.services import send_confirmation_email, send_recovery_token
from .serializers import UserSerializer, EarlyAccessRequestSerializer, IdentitySerializer, OTTRequestSerializer, \
    RecoverySerializer

logger = logging.getLogger("api")


class TokenView(ObtainJSONWebToken):
    def post(self, request):
        data = dict(username=request.data.get('username'), password=request.data.get('password'))
        if 'username' in data:
            data['username'] = str(data['username']).lower()
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            token = serializer.object.get('token')
            response_data = {
                "token": token,
                "email": user.email,
                "username": user.username,
                "namespaces": [user.namespace.name],
            }
            logger.debug("User logged in successfully: {}".format(data['username']))
            return Response(response_data)
        logger.warning("User logging failure: {}".format(data['username']))
        return GeneralResponse(_("Username or password is wrong"), status=status.HTTP_400_BAD_REQUEST)


class EarlyAccessView(APIView):
    def post(self, request):
        serialized = EarlyAccessRequestSerializer(data=request.data)
        if serialized.is_valid():
            try:
                serialized.save()
                return GeneralResponse(_("Your early access request registered successfully."))
            except Exception as e:
                logger.error("Error in early access registration. {}".format(e))
                logger.error("Error occurred in saving  early access request. email is: {}".format(
                    serialized.validated_data['email']))
                return ErrorResponse(serialized.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return ErrorResponse(serialized.errors, status=status.HTTP_400_BAD_REQUEST)


class AccountView(APIView):
    def post(self, request):
        serialized = UserSerializer(data=request.data)
        if serialized.is_valid():
            u = serialized.save(first_name='', last_name='', is_active=False, )
            send_confirmation_email(u)

            logger.debug(
                "New user registered successfully: {}".format(serialized.validated_data['username'])
            )
            return GeneralResponse(_(
                "Your account has been created successfully, You need to activate your account using the link we send you"),
                status=status.HTTP_201_CREATED)
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
            logger.debug("User has been activated: id: {}".format(serializer.validated_data['id']))
            return GeneralResponse(_("Your account has been activated"))
        except ActivationCode.DoesNotExist:
            return GeneralResponse(_("Requested code does not exist"), status=404)
        except ValidationError:
            return GeneralResponse(_("Invalid request"), status=400)


class OnetimeTokenView(APIView):
    def post(self, request):
        serializer = OTTRequestSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            send_recovery_token(serializer.validated_data['user'])
            logger.debug("Request for an OTT has been received: {}".format(serializer.validated_data['identifier']))
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
                password=make_password(serializer.validated_data['new_password']),
                is_active=True
            )
            logger.debug("User's password has been changed using an OTT : uid:{}".format(
                serializer.validated_data['id'])
            )
            return GeneralResponse(_("Your password has been changed"))
        except RecoveryToken.DoesNotExist:
            return GeneralResponse(_("Requested code does not exist"), status=404)
        except ValidationError:
            return GeneralResponse(_("Invalid request"), status=400)
