# Create your views here.
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

#
from image.image_builder import trigger_image_building
from image.image_deployer import deploy, logs, destroy
from user.util import ClientInfo
from .serializers import *


class AppView(APIView):
    def get(self, request):
        client = ClientInfo(request)
        if client.is_anonymous():
            return Response("You need to login first.", status.HTTP_401_UNAUTHORIZED)
        apps = client.user.apps
        data = AppSerializer(instance=apps, many=True).data
        return Response(data)

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
        if WebApp.objects.filter(name=app_name).exists():
            versions = AppVersion.objects.filter(app=app_name)
            data = AppVersionSerializer(instance=versions, many=True).data
            return Response(data)
        return Response("App with name {} does not exist.".format(app_name), status=status.HTTP_404_NOT_FOUND)


class BuildView(APIView):
    def get(self, request, app_name, app_version):
        client = ClientInfo(request)
        if client.is_anonymous():
            return Response("You need to login first.", status.HTTP_401_UNAUTHORIZED)

        version = AppVersion.objects.filter(app=app_name, version=app_version, app__owner=client.user).first()
        if not version:
            return Response("Couldn't find the resource", status.HTTP_404_NOT_FOUND)
        build = version.builds.first()
        if build:
            data = BuildSerializer(build).data
            return Response(data)
        return Response("Couldn't find the resource", status=status.HTTP_404_NOT_FOUND)


class ServiceListView(APIView):
    def get(self, request):
        client = ClientInfo(request)
        if client.is_anonymous():
            return Response("You need to login first.", status.HTTP_401_UNAUTHORIZED)

        services = Service.objects.filter(owner=client.user.id).all()
        data = CreatedServiceSerializer(instance=services, many=True).data
        return Response(data)

    def post(self, request):
        client = ClientInfo(request)
        if client.is_anonymous():
            return Response("You need to login first.", status.HTTP_401_UNAUTHORIZED)
        serializer = ServiceSerializer(data=request.data)
        if serializer.is_valid():
            app_name = serializer.validated_data['app_name']
            img_version = serializer.validated_data['img_version']
            service_name = serializer.validated_data.get('service_name')
            container = deploy(app_name, img_version, service_name, client.user)
            data = ContainerSerializer(instance=container).data
            return Response(data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ServiceView(APIView):
    def delete(self, request, service_name):
        client = ClientInfo(request)
        if client.is_anonymous():
            return Response("You need to login first.", status.HTTP_401_UNAUTHORIZED)
        destroy(service_name, client.user)
        return Response("Service destroyed successfully.")


class ServiceLogView(APIView):
    def get(self, request, service_id):
        return Response(logs(service_id))

# curl -XPOST http://localhost:8000/api/webapp/apps/app1/versions -F "version=v1" -F "source=@/Users/SOROOSH/projects/fandogh/fandogh/examples/nodejs-app.zip" -H "filename: image" -v
