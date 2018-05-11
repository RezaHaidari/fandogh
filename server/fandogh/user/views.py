import logging

from django.contrib.auth.models import User
from django.http import QueryDict
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.views import ObtainJSONWebToken

from common.response import ErrorResponse, GeneralResponse
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
                error_logger.error("Error occured in saving  early access request. email is: {}".format(serialized.validated_data['email']))

        else:
            return ErrorResponse(serialized.errors, status=status.HTTP_400_BAD_REQUEST)


class AccountView(APIView):
    def post(self, request):
        serialized = UserSerializer(data=request.data)
        if serialized.is_valid():
            try:
                u = User.objects.create_user(
                    email=serialized.initial_data['email'],
                    username=serialized.initial_data['email'],
                    password=serialized.initial_data['password'],
                    first_name='',
                    last_name=''
                )
                if u:
                    return Response("User has been registered successfully", status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response("A user with current email exists", status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)
