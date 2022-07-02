import boto3
import uuid


from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from ..functions.custom_renderers import JPEGRenderer, PNGRenderer
from django.conf import settings

from ..models import Image
from ..serializers.media_serializers import (ImageSerializer,
                                             ImageDetailSerializer)


class ImageView(APIView):
    def get(self, request):
        images = Image.objects.all().order_by('-updated')
        serializer = ImageSerializer(images,
                                     many=True,
                                     context={'request': request})
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        if request.data['image']:
            orig_name = request.data['image'].name
            api_id = str(uuid.uuid4())
            request.data['image'].name = api_id + \
                '.' + orig_name.split('.')[-1]

            image = Image.objects.create(
                api_id=api_id,
                image=request.data['image'],
                title=orig_name,
                caption=request.data.get('caption', None),
            )
            serializer = ImageDetailSerializer(
                image,
                context={'request': request}
            )

            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class ImageDetailView(APIView):
    def get(self, request, api_id):
        try:
            images = Image.objects.get(api_id=api_id)
        except Image.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ImageDetailSerializer(images,
                                           context={'request': request})
        return Response(serializer.data)

    def delete(self, request, api_id):
        image = Image.objects.get(api_id=api_id)

        session = boto3.session.Session()
        client = session.client(
            's3',
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY
            )

        # Failed Storage deletion will not do anything
        client.delete_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=f'{settings.MEDIAFILES_LOCATION}/{image.image.name}'
            )

        # Delete image link in database
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ImageRenderView(APIView):
    renderer_classes = [JPEGRenderer, PNGRenderer]
    authentication_classes = []

    def get(self, request, api_id, media_type):
        image = Image.objects.get(api_id=api_id)

        return Response(image.image, status=status.HTTP_200_OK)
