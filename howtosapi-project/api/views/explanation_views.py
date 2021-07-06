from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import Explanation
from ..serializers import ExplanationSerializer, ExplanationDetailSerializer


class ExplanationView(APIView):
    """
    View to Explanation Text Detail
    """
    def get(self, request):
        explanations = Explanation.objects.all().order_by('-id')
        serializer = ExplanationSerializer(explanations,
                                           many = True,
                                           context = {'request': request})
        return Response(serializer.data)
    
    def post(self, request, format = None):
        serializer = ExplanationSerializer(data = request.data,
                                     context = {'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status = status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status = status.HTTP_400_BAD_REQUEST)

class ExplanationDetailView(APIView):
    """
    View to Explanation Detail
    """
    def get(self, request, uri_id):
        explanation = Explanation.objects.get(explanationuriid__uri_id = uri_id)
        serializer = ExplanationDetailSerializer(explanation,
                                                 context = {'request': request})
        return Response(serializer.data)

    def patch(self, request, uri_id):
        explanation = Explanation.objects.get(explanationuriid__uri_id = uri_id)
        serializer = ExplanationDetailSerializer(explanation,
                                          data = request.data,
                                          partial = True,
                                          context = {'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status = status.HTTP_200_OK)
        return Response(serializer.errors,
                        status = status.HTTP_400_BAD_REQUEST)

    def delete(self, request, uri_id):
        Explanation.objects.get(explanationuriid__uri_id = uri_id).delete()
        return Response(status = status.HTTP_204_NO_CONTENT)
