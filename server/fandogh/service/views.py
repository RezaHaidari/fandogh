# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

#
from image.k8s_deployer import deploy, destroy, logs
from image.models import ImageVersion
from user.util import ClientInfo
from .serializers import *


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
            image_name = serializer.validated_data['image_name']
            image_version = serializer.validated_data['image_version']
            service_name = serializer.validated_data.get('service_name')
            env_variables = serializer.validated_data.get('environment_variables')
            port = serializer.validated_data.get('port', 80)
            running_services = Service.objects.filter(owner=client.user, state='RUNNING').exclude(
                name=service_name).all()
            # TODO: a quick check for releasing alpha version
            if len(running_services) > 1 and client.user.username != 'soroosh@yahoo.com':
                return Response(
                    "You already have 2 or more running services. Please destroy one of the previous ones if you want to deploy a new one.",
                    status=status.HTTP_400_BAD_REQUEST)

            version = ImageVersion.objects.filter(image__name=image_name, version=image_version,
                                                  image__owner=client.user).first()
            if version:
                if version.state == 'BUILT':
                    service = deploy(image_name, image_version, service_name, client.user, env_variables, port)
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
