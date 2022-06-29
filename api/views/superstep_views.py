
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from api.serializers.superstep_serializer import SuperStepSerializer


class SuperStepView(APIView):
    def post(self, request):
        serializer = SuperStepSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
