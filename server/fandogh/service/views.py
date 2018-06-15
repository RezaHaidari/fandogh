# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.response import GeneralResponse
from service.managed_services.mysql import get_deployer
from .k8s_deployer import deploy, destroy, logs, get_services
from image.models import ImageVersion
from user.util import ClientInfo
from .serializers import *


class ManagedServiceListView(APIView):
    def post(self, request):
        client = ClientInfo(request)
        if client.is_anonymous():
            return Response("You need to login first.", status.HTTP_401_UNAUTHORIZED)
        service_name = 'mysql'
        variate = '5.7'

        get_deployer(service_name).deploy(variate, {})

        return GeneralResponse("Service deployed")


class ServiceListView(APIView):
    def get(self, request):
        client = ClientInfo(request)
        if client.is_anonymous():
            return Response("You need to login first.", status.HTTP_401_UNAUTHORIZED)
        data = get_services(client.user)

        return Response(ServiceResponseSerializer(instance=data, many=True).data)

    def post(self, request):
        client = ClientInfo(request)
        if client.is_anonymous():
            return Response("You need to login first.", status.HTTP_401_UNAUTHORIZED)
        serializer = ServiceSerializer(data=request.data)
        if serializer.is_valid():
            image_name = serializer.validated_data['image_name']
            image_name = client.user.namespace.name + '/' + image_name
            image_version = serializer.validated_data['image_version']
            service_name = serializer.validated_data.get('service_name')
            env_variables = serializer.validated_data.get('environment_variables')
            port = serializer.validated_data.get('port', 80)
            internal = serializer.validated_data.get('internal', False)
            running_services = get_services(client.user)
            # TODO: a quick check for releasing alpha version
            if len(running_services) > 1 and list(filter(lambda service: service.get('name', '') == service_name,
                                                         running_services)) == 0 and client.user.username != 'soroosh@yahoo.com':
                return Response(
                    "You already have 2 or more running services. Please destroy one of the previous ones if you want to deploy a new one.",
                    status=status.HTTP_400_BAD_REQUEST)

            version = ImageVersion.objects.filter(image__name=image_name,
                                                  version=image_version,
                                                  state='BUILT',
                                                  image__owner=client.user).first()
            if version:
                service = deploy(image_name, image_version, service_name, client.user, env_variables, port, internal)
            else:
                return Response('Could not find a successfully built image with the given name and version',
                                status=status.HTTP_404_NOT_FOUND)

            data = ServiceResponseSerializer(
                instance=service).data
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
        client = ClientInfo(request)
        if client.is_anonymous():
            return Response("You need to login first.", status.HTTP_401_UNAUTHORIZED)

        return Response(logs(service_name, client.user))
