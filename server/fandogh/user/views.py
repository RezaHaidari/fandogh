import logging

from django.contrib.auth.models import User
from django.db.transaction import atomic
from django.http import QueryDict
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.views import ObtainJSONWebToken

from common.response import ErrorResponse, GeneralResponse
from user.models import Namespace
from user.services import send_confirmation_email
from .serializers import UserSerializer, EarlyAccessRequestSerializer

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

        return Response("Username or password is wrong", status=status.HTTP_400_BAD_REQUEST)


class EarlyAccessView(APIView):
    def post(self, request):
        serialized = EarlyAccessRequestSerializer(data=request.data)
        if serialized.is_valid():
            try:
                serialized.save()
                return GeneralResponse("Your early access request registered successfully.")
            except Exception as e:
                error_logger.error("Error in early access registration. {}".format(e))
                error_logger.error("Error occured in saving  early access request. email is: {}".format(serialized.validated_data['email']))
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
                        last_name=''
                    )
                    if u:
                        Namespace.objects.create(name=serialized.validated_data['namespace'], owner=u)
                        send_confirmation_email(u)
                        return GeneralResponse("User has been registered successfully", status=status.HTTP_201_CREATED)
            except Exception as e:
                print(e)
                return ErrorResponse("A user with current email or namespace exists", status=status.HTTP_400_BAD_REQUEST)
        else:
            return ErrorResponse(serialized.errors, status=status.HTTP_400_BAD_REQUEST)
