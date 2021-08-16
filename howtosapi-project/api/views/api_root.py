from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse


class APIRoot(APIView):
    def get(self, request):
        return Response({
            'statistics': reverse('statistics', request=request),
            'howtos': reverse('how-to-list', request=request),
            'steps': reverse('step-list', request=request),
            'explanations': reverse('explanation', request=request),
            'images': reverse('images', request=request),
            'howto_guides' : reverse('howto-guide-list', request=request),
            'step_guides' : reverse('step-guide-list', request=request),
        })
