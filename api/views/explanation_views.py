from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import Explanation
from ..serializers.explanation_serializers import (ExplanationSerializer,
                                                   ExplanationDetailSerializer)


class ExplanationView(APIView):
    def get(self, request):
        explanations = Explanation.objects.all().order_by('-updated')
        serializer = ExplanationSerializer(explanations,
                                           many=True,
                                           context={'request': request})
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ExplanationSerializer(data=request.data,
                                           context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class ExplanationDetailView(APIView):
    def get(self, request, api_id):
        try:
            explanation = Explanation.objects.get(api_id=api_id)
        except Explanation.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ExplanationDetailSerializer(explanation,
                                                 context={'request': request})
        return Response(serializer.data)

    def patch(self, request, api_id):
        explanation = Explanation.objects.get(api_id=api_id)
        serializer = ExplanationDetailSerializer(explanation,
                                                 data=request.data,
                                                 partial=True,
                                                 context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_200_OK)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, api_id):
        Explanation.objects.get(api_id=api_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
