from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse


class APIRoot(APIView):
    def get(self, request):
        return Response({
            'statistics': reverse('api:statistics', request=request),
            'sequence': reverse('api:sequence-list', request=request),
            'steps': reverse('api:step-list', request=request),
            # 'explanations': reverse('explanation', request=request),
            # 'images': reverse('images', request=request),
            # 'sequence_guides' : reverse('sequence-guide-list', request=request),
            # 'step_guides' : reverse('step-guide-list', request=request),
        })
