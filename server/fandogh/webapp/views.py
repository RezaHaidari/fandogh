from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
#
from image import trigger_image_building
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
    parser_classes = (MultiPartParser,)

    def post(self, request, app_name):
        source_file = request.FILES.get('source', None)
        version = request.data.get('version', None)
        if version:
            app_version = AppVersion(app_id=app_name, version=version, source=source_file)
            app_version.save()
            trigger_image_building(app_version)
            return Response("Version created successfully")
        return Response("version is necessary")

# curl -XPOST http://localhost:8000/api/webapp/apps/app1/versions -F "version=v1" -F "source=@/Users/SOROOSH/projects/fandogh/fandogh/examples/nodejs-app.zip" -H "filename: image" -v
