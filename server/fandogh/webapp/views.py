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
        client = ClientInfo(request)
        if client.is_anonymous():
            return Response("You need to login first.", status.HTTP_401_UNAUTHORIZED)
        request_data = request.data.copy()
        request_data['owner'] = client.user.id
        serializer = AppSerializer(data=request_data)

        if serializer.is_valid():
            serializer.save()
            return Response("App created successfully")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VersionView(APIView):
    parser_classes = (MultiPartParser,)

    def post(self, request, app_name):
        source_file = request.FILES.get('source', None)
        # TODO: authenticate user
        # TODO: validate version
        version = request.data.get('version', None)
        if version:
            app_version = AppVersion(app_id=app_name, version=version, source=source_file)
            app_version.save()
            trigger_image_building(app_version)
            return Response("Version created successfully")
        return Response("version is necessary", status=status.HTTP_400_BAD_REQUEST)

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
            env_variables = serializer.validated_data.get('environment_variables')
            running_services = Service.objects.filter(owner=client.user, state='RUNNING').exclude(
                name=service_name).all()
            # TODO: a quick check for releasing alpha version
            if len(running_services) > 1 and client.user.username != 'soroosh@yahoo.com':
                return Response(
                    "You already have 2 or more running services. Please destroy one of the previous ones if you want to deploy a new one.",
                    status=status.HTTP_400_BAD_REQUEST)

            version = AppVersion.objects.filter(app__name=app_name, version=img_version, app__owner=client.user).first()
            if version:
                if version.state == 'BUILT':
                    service = deploy(app_name, img_version, service_name, client.user, env_variables)
                else:
                    # TODO: different message for different states
                    return Response('version has not been build successfully.', status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response('Application or version does not exist.', status=status.HTTP_404_NOT_FOUND)

            data = ContainerSerializer(instance=service).data
            return Response(data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ServiceView(APIView):
    def delete(self, request, service_name):
        client = ClientInfo(request)
        if client.is_anonymous():
            return Response("You need to login first.", status.HTTP_401_UNAUTHORIZED)
        destroyed = destroy(service_name, client.user)
        if destroyed:
            return Response("Service destroyed successfully.")
        else:
            return Response("No service with name {} running".format(service_name))


class ServiceLogView(APIView):
    def get(self, request, service_name):
        service = Service.objects.filter(name=service_name).first()
        if not service:
            return Response("Resource not found", status=404)
        return Response(logs(service.name))
