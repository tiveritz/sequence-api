from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from ..functions.uri_id import generate_uri_id

from ..models import Image
from ..serializers.media_serializers import ImageSerializer

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
            uri_id = generate(request.data['image'].size)
            request.data['image'].name = uri_id + '.' + orig_name.split('.')[-1]

            Image.objects.create(
                uri_id=uri_id,
                image=request.data['image'],
                title=orig_name,
                caption=request.data.get('caption', None),
            )
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)
