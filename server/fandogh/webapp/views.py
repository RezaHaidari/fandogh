from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AppVersion
from .serializers import AppSerializer


class AppView(APIView):
    def post(self, request):
        serializer = AppSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response("App created successfully")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VersionView(APIView):
    def post(self, request, app_name):
        version = request.data.get('version', None)
        if version:
            app_version = AppVersion(app_id=app_name, version=version)
            app_version.save()
            return Response("Version created successfully")
        return Response("version is necessary")
