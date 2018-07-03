# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from service.managed_services.mysql import get_deployers
from .k8s_deployer import deploy, destroy, logs, get_services
from image.models import ImageVersion
from user.util import ClientInfo
from .serializers import *
import logging

logger = logging.getLogger("api")


class ManagedServiceListView(APIView):
    def get(self, request):
        client = ClientInfo(request)
        if client.is_anonymous():
            return Response("You need to login first.", status.HTTP_401_UNAUTHORIZED)
        return Response(get_deployers(), status=status.HTTP_200_OK)

    def post(self, request):
        client = ClientInfo(request)
        if client.is_anonymous():
            return Response("You need to login first.", status.HTTP_401_UNAUTHORIZED)

        serializer = ManagedServiceSerializer(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data['name']
            version = serializer.validated_data['version']
            context = {
                'namespace': client.user.namespace.name,
                'service_name': serializer.validated_data['name'],
                'version': serializer.validated_data['version']
            }
            user_config = serializer.validated_data['config']
            if user_config:
                context.update(user_config)

            deploy_result = get_deployer(name).deploy(version, context)
            logger.debug("New Managed service has been created, Context:{} ".format(
                context
            ))
            return Response(deploy_result)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
            service_type = serializer.validated_data.get('service_type', 'external')
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
                service = deploy(image_name, image_version, service_name, client.user, env_variables, port,
                                 service_type)
            else:
                return Response('Could not find a successfully built image with the given name and version',
                                status=status.HTTP_404_NOT_FOUND)

            logger.debug("New service has been created, Image name: {}  ".format(image_name))
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
            logger.debug("service {} has been deleted by user {} ".format(service_name, request.user.username))
            return Response("Service destroyed successfully.")
        else:
            return Response("No service with name {} running".format(service_name))


class ServiceLogView(APIView):
    def get(self, request, service_name):
        client = ClientInfo(request)
        if client.is_anonymous():
            return Response("You need to login first.", status.HTTP_401_UNAUTHORIZED)

        return Response(logs(service_name, client.user))
