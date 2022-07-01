
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveDestroyAPIView
from rest_framework.response import Response
from core.pagination import ListPagination

from api.models import Sequence

from api.serializers.sequence_serializers import SequenceSerializer


class SequenceView(RetrieveDestroyAPIView):
    def get(self, request, uuid):
        sequence = Sequence.objects.get(uuid=uuid)
        serializer = SequenceSerializer(sequence, context={'request': request})
        return Response(serializer.data)

    def delete(self, request, uuid):
        try:
            Sequence.objects.get(uuid=uuid).delete()
        except Sequence.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SequenceListView(ListCreateAPIView):
    queryset = Sequence.objects.all().order_by('-updated')
    serializer_class = SequenceSerializer
    pagination_class = ListPagination

    def post(self, request, format=None):
        serializer = SequenceSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
