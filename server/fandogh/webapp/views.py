# Create your views here.
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

#
from image.image_builder import trigger_image_building
from image.image_deployer import deploy, logs
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
        # TODO: validate version
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


class DeployView(APIView):
    def post(self, request):
        serializer = DeploymentSerializer(data=request.data)
        if serializer.is_valid():
            app_name = serializer.validated_data['app_name']
            img_version = serializer.validated_data['img_version']
            container = deploy(app_name, img_version)
            data = ContainerSerializer(instance=container).data
            return Response(data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContainerLogView(APIView):
    def get(self, request, container_id):
        return Response(logs(container_id))

# curl -XPOST http://localhost:8000/api/webapp/apps/app1/versions -F "version=v1" -F "source=@/Users/SOROOSH/projects/fandogh/fandogh/examples/nodejs-app.zip" -H "filename: image" -v
