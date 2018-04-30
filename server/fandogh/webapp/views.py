# Create your views here.
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

#
from image.image_builder import trigger_image_building
from image.models import Build
from .models import AppVersion
from .serializers import *


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

    def get(self, request, app_name):
        versions = AppVersion.objects.filter(app=app_name)
        data = AppVersionSerializer(instance=versions, many=True).data
        return Response(data)


class BuildView(APIView):
    def get(self, request, app_name, app_version):
        build = Build.objects.filter(version__app=app_name, version=app_version).first()
        if build:
            data = BuildSerializer(build).data
            return Response(data)
        return Response("Not found", status=status.HTTP_404_NOT_FOUND)

# curl -XPOST http://localhost:8000/api/webapp/apps/app1/versions -F "version=v1" -F "source=@/Users/SOROOSH/projects/fandogh/fandogh/examples/nodejs-app.zip" -H "filename: image" -v
