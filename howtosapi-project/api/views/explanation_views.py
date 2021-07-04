from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import Explanation
from ..serializers import ExplanationSerializer, ExplanationDetailSerializer


class ExplanationView(APIView):
    """
    View to Explanation Text Detail
    """
    def get(self, request):
        explanations = Explanation.objects.all()
        serializer = ExplanationSerializer(explanations,
                                           many = True,
                                           context = {'request': request})
        return Response(serializer.data)

class ExplanationDetailView(APIView):
    """
    View to Explanation Detail
    """
    def get(self, request, uri_id):
        explanation = Explanation.objects.get(explanationuriid__uri_id = uri_id)
        serializer = ExplanationDetailSerializer(explanation,
                                                 context = {'request': request})
        return Response(serializer.data)
'''
class ExplanationTextView(APIView):
    """
    View to Explanation Texts
    """
    def get(self, request):
        explanations = Explanation.objects.all()
        serializer = ExplanationSerializer(explanations,
                                           many = True,
                                           context = {'request': request})
        return Response(serializer.data)

class ExplanationCodeView(APIView):
    """
    View to Explanation Codes
    """
    def get(self, request):
        explanations = Explanation.objects.all()#filter(type = 'code')
        serializer = ExplanationSerializer(explanations,
                                           many = True,
                                           context = {'request': request})
        return Response(serializer.data)
'''