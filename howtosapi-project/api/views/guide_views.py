from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from ..models import (GuideHowTo,
                      GuideStep)

from ..serializers.guide_serializers import (HowToGuideSerializer,
                                             StepGuideSerializer,)


class HowToGuideListView(APIView):
    """
    View to How To Guide List
    """
    def get(self, request):
        guide_howto = GuideHowTo.objects.all()
        serializer = HowToGuideSerializer(guide_howto,
                                          many=True,
                                          context={'request' : request})
        return Response(serializer.data)


class StepGuideListView(APIView):
    """
    View to Step Guide List
    """
    def get(self, request):
        guide_step = GuideStep.objects.all()
        serializer = StepGuideSerializer(guide_step,
                                         many=True,
                                         context={'request' : request})
        return Response(serializer.data)


class HowToGuideView(APIView):
    """
    View to How To Guide
    """
    def get(self, request, uri_id):
        guide_howto = GuideHowTo.objects.get(uri_id=uri_id)
        serializer = HowToGuideSerializer(guide_howto,
                                          context={'request' : request})
        return Response(serializer.data)


class StepGuideView(APIView):
    """
    View to Step Guide
    """
    def get(self, request, howto_uri_id, step_uri_id, ref_id):
        try:
            guide_step = GuideStep.objects.get(uri_id=step_uri_id, ref_id=ref_id)
        except GuideStep.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = StepGuideSerializer(guide_step,
                                         context={'request' : request})
        return Response(serializer.data)