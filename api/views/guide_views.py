from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import re

from ..models import (SequenceGuide,
                      SequenceGuideStep,
                      Image)

from ..serializers.guide_serializers import (SequenceGuideSerializer,
                                             StepGuideSerializer,)


class SequenceGuideListView(APIView):
    """
    View to Sequence Guide List
    """

    def get(self, request, space):
        spaces_dict = {
            'test': 'TST',
            'preview': 'PRV',
            'public': 'PBL',
            'private': 'PRV',
        }
        guide_sequence = SequenceGuide.objects.filter(space=spaces_dict[space])
        serializer = SequenceGuideSerializer(guide_sequence,
                                          many=True,
                                          context={'request': request})
        return Response(serializer.data)

'''
class StepGuideListView(APIView):
    """
    View to Step Guide List
    """

    def get(self, request):
        guide_step = SequenceGuideStep.objects.all()
        serializer = StepGuideSerializer(guide_step,
                                         many=True,
                                         context={'request': request})
        return Response(serializer.data)
'''


class SequenceGuideView(APIView):
    """
    View to Sequence Guide
    """

    def get(self, request, api_id, space):
        spaces_dict = {
            'test': 'TST',
            'preview': 'PRV',
            'public': 'PBL',
            'private': 'PRV',
        }
        guide_sequence = SequenceGuide.objects.get(
            api_id=api_id, space=spaces_dict[space])
        serializer = SequenceGuideSerializer(guide_sequence,
                                          context={'request': request})
        return Response(serializer.data)


class StepGuideView(APIView):
    """
    View to Step Guide
    """

    def get(self, request, step_api_id):
        try:
            guide_step = SequenceGuideStep.objects.get(
                api_id=step_api_id)
        except SequenceGuideStep.DoesNotExist:
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
                image = Image.objects.get(api_id=image_id)
                replace = '[[img|' + image_id + ']]'
                content = content.replace(replace, image.image.url)
        return content
