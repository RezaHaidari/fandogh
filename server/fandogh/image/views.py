import logging
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy
from django.db import IntegrityError
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from common.response import ErrorResponse
from image.image_builder import trigger_image_building
from image.models import ImageVersion, Image
from image.serializers import ImageSerializer, ImageVersionSerializer, ImmageBuildSerializer
from user.util import ClientInfo

logger = logging.getLogger("api")
UnAuthorizedResponse = Response(ugettext_lazy("You need to login first."), status.HTTP_401_UNAUTHORIZED)


class ImageView(APIView):
    def get(self, request):
        client = ClientInfo(request)
        if client.is_anonymous():
            return UnAuthorizedResponse
        images = client.user.images
        data = ImageSerializer(instance=images, many=True).data
        return Response(data)

    def post(self, request):
        client = ClientInfo(request)
        if client.is_anonymous():
            return UnAuthorizedResponse
        request_data = request.data.copy()
        request_data['owner'] = client.user.id
        serializer = ImageSerializer(data=request_data)
        serializer.initial_data['name'] = client.user.namespace.name + '/' + serializer.initial_data['name']
        if serializer.is_valid():
            serializer.save()
            logger.debug("Image has been successfully created by {} on {} namespace".format(
                client.user.username, client.user.namespace.name
            ))
            return Response(_("Image created successfully"))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ImageVersionView(APIView):
    parser_classes = (MultiPartParser,)

    def post(self, request, image_name):
        source_file = request.FILES.get('source', None)
        client = ClientInfo(request)
        if client.is_anonymous():
            return UnAuthorizedResponse

        image_name = client.user.namespace.name + '/' + image_name
        try:
            image = Image.objects.get(name=image_name)
            if image.owner.username != client.user.username:
                return ErrorResponse(_("You cannot publish version for this image"), status=status.HTTP_403_FORBIDDEN)

        except Image.DoesNotExist as e:
            return ErrorResponse(_("Image with this name: {} does not exist").format(image_name),
                                 status=status.HTTP_404_NOT_FOUND)

        version = request.data.get('version', None)
        try:
            if version:
                existing_version = ImageVersion.objects.filter(image_id=image_name, version=version).first()
                if existing_version and existing_version.state == 'BUILT':
                    return ErrorResponse(
                        _("You already have a successful image built with version:{} for image:{} ").format(version,
                                                                                                         image_name),
                        status=status.HTTP_400_BAD_REQUEST)

                app_version = ImageVersion(image_id=image_name, version=version, source=source_file)
                app_version.save()
                trigger_image_building(app_version)
                logger.debug("New ImageVersion has been successfully created by {} for {}".format(
                    client.user.username, image_name,
                ))
                return Response(_("Version created successfully"))
        except IntegrityError:
            return Response(_("Image not found"), status=404)
        return Response(_("version is necessary"), status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, image_name):
        client = ClientInfo(request)
        if client.is_anonymous():
            return UnAuthorizedResponse
        image_name = client.user.namespace.name + '/' + image_name
        if Image.objects.filter(name=image_name, owner=client.user).exists():
            versions = ImageVersion.objects.filter(image=image_name)
            data = ImageVersionSerializer(instance=versions, many=True).data
            return Response(data)
        return Response(_("Image with name {} does not exist.").format(image_name), status=status.HTTP_404_NOT_FOUND)


class ImageBuildView(APIView):
    def get(self, request, image_name, image_version):
        client = ClientInfo(request)
        if client.is_anonymous():
            return UnAuthorizedResponse

        image_name = client.user.namespace.name + '/' + image_name
        version = ImageVersion.objects.filter(image=image_name, version=image_version, image__owner=client.user).last()
        if not version:
            return Response(_("Couldn't find the resource"), status.HTTP_404_NOT_FOUND)
        build = version.builds.first()
        if build:
            data = ImmageBuildSerializer(build).data
            return Response(data)
        return Response(_("Couldn't find the resource"), status=status.HTTP_404_NOT_FOUND)
