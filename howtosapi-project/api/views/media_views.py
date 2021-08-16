from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from ..functions.uri_id import generate_uri_id
from ..functions.custom_renderers import JPEGRenderer, PNGRenderer

from ..models import Image
from ..serializers.media_serializers import ImageSerializer, ImageDetailSerializer

class ImageView(APIView):
    """
    View to Images
    """
    def get(self, request):
        images = Image.objects.all().order_by('-updated')
        serializer = ImageSerializer(images,
                                     many=True,
                                     context={'request' : request})
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        if request.data['image']:
            orig_name = request.data['image'].name
            uri_id = generate_uri_id()
            request.data['image'].name = uri_id + '.' + orig_name.split('.')[-1]

            image = Image.objects.create(
                uri_id=uri_id,
                image=request.data['image'],
                title=orig_name,
                caption=request.data.get('caption', None),
            )
            serializer = ImageDetailSerializer(
                image,
                context={'request' : request}
                )

            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class ImageRenderView(APIView):
    """
    Image Render
    """
    renderer_classes = [JPEGRenderer, PNGRenderer]
    authentication_classes = []

    def get(self, request, uri_id, media_type):
        image = Image.objects.get(uri_id=uri_id)

        return Response(image.image, status=status.HTTP_200_OK)