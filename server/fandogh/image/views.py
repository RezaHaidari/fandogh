from django.db import IntegrityError
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from image.image_builder import trigger_image_building
from image.models import ImageVersion, Image
from image.serializers import ImageSerializer, ImageVersionSerializer, ImmageBuildSerializer
from user.util import ClientInfo


class ImageView(APIView):
    def get(self, request):
        client = ClientInfo(request)
        if client.is_anonymous():
            return Response("You need to login first.", status.HTTP_401_UNAUTHORIZED)
        images = client.user.images
        data = ImageSerializer(instance=images, many=True).data
        return Response(data)

    def post(self, request):
        client = ClientInfo(request)
        if client.is_anonymous():
            return Response("You need to login first.", status.HTTP_401_UNAUTHORIZED)
        request_data = request.data.copy()
        request_data['owner'] = client.user.id
        serializer = ImageSerializer(data=request_data)

        if serializer.is_valid():
            serializer.save()
            return Response("Image created successfully")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ImageVersionView(APIView):
    parser_classes = (MultiPartParser,)

    def post(self, request, image_name):
        source_file = request.FILES.get('source', None)
        # TODO: authenticate user
        # TODO: validate version
        version = request.data.get('version', None)
        try:
            if version:
                app_version = ImageVersion(image_id=image_name, version=version, source=source_file)
                app_version.save()
                trigger_image_building(app_version)
                return Response("Version created successfully")
        except IntegrityError:
            return Response("Image not found", status=404)
        return Response("version is necessary", status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, image_name):
        if Image.objects.filter(name=image_name).exists():
            versions = ImageVersion.objects.filter(image=image_name)
            data = ImageVersionSerializer(instance=versions, many=True).data
            return Response(data)
        return Response("Image with name {} does not exist.".format(image_name), status=status.HTTP_404_NOT_FOUND)


class ImageBuildView(APIView):
    def get(self, request, image_name, image_version):
        client = ClientInfo(request)
        if client.is_anonymous():
            return Response("You need to login first.", status.HTTP_401_UNAUTHORIZED)

        version = ImageVersion.objects.filter(image=image_name, version=image_version, image__owner=client.user).first()
        if not version:
            return Response("Couldn't find the resource", status.HTTP_404_NOT_FOUND)
        build = version.builds.first()
        if build:
            data = ImmageBuildSerializer(build).data
            return Response(data)
        return Response("Couldn't find the resource", status=status.HTTP_404_NOT_FOUND)