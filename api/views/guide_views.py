from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import re

from ..models import (HowToGuide,
                      HowToGuideStep,
                      Image)

from ..serializers.guide_serializers import (HowToGuideSerializer,
                                             StepGuideSerializer,)


class HowToGuideListView(APIView):
    """
    View to How To Guide List
    """

    def get(self, request, space):
        spaces_dict = {
            'test': 'TST',
            'preview': 'PRV',
            'public': 'PBL',
            'private': 'PRV',
        }
        guide_howto = HowToGuide.objects.filter(space=spaces_dict[space])
        serializer = HowToGuideSerializer(guide_howto,
                                          many=True,
                                          context={'request': request})
        return Response(serializer.data)


class StepGuideListView(APIView):
    """
    View to Step Guide List
    """

    def get(self, request):
        guide_step = HowToGuideStep.objects.all()
        serializer = StepGuideSerializer(guide_step,
                                         many=True,
                                         context={'request': request})
        return Response(serializer.data)


class HowToGuideView(APIView):
    """
    View to How To Guide
    """

    def get(self, request, uri_id, space):
        spaces_dict = {
            'test': 'TST',
            'preview': 'PRV',
            'public': 'PBL',
            'private': 'PRV',
        }
        guide_howto = HowToGuide.objects.get(
            howto_uri_id=uri_id, space=spaces_dict[space])
        serializer = HowToGuideSerializer(guide_howto,
                                          context={'request': request})
        return Response(serializer.data)


class StepGuideView(APIView):
    """
    View to Step Guide
    """

    def get(self, request, howto_uri_id, step_uri_id, ref_id):
        try:
            guide_step = HowToGuideStep.objects.get(
                uri_id=step_uri_id, ref_id=ref_id)
        except HowToGuideStep.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = StepGuideSerializer(guide_step,
                                         context={'request': request})
        serialized_data = serializer.data
        serialized_data['content'] = self.insert_media_url(
            serialized_data['content'])
        return Response(serialized_data)

    def insert_media_url(self, content):
        # It is required to generate the media urls every time. Reaseon is that
        # media is serverd over AWS Bucket
        pattern = re.compile(r'(?:\[\[img\|)([a-z0-9]{8})(?:\]\])') or False
        image_ids = re.findall(pattern, content)

        if image_ids:
            for image_id in image_ids:
                image = Image.objects.get(uri_id=image_id)
                replace = '[[img|' + image_id + ']]'
                content = content.replace(replace, image.image.url)
        return content
