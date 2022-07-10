from core.pagination import ListPagination

from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListCreateAPIView, RetrieveDestroyAPIView
from rest_framework.response import Response

from api.filters import SequenceSearchFilter, SequenceOrderingFilter
from api.models import Sequence

from api.serializers.sequence_serializers import (SequenceDetailSerializer,
                                                  SequenceSerializer)


class SequenceDetailView(RetrieveDestroyAPIView):
    def get(self, request, uuid):
        sequence = Sequence.objects.get(uuid=uuid)
        serializer = SequenceDetailSerializer(sequence,
                                              context={'request': request})
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
    filter_backends = [SequenceSearchFilter, SequenceOrderingFilter]
    search_fields = ['title']
    ordering_fields = ['title', 'updated', 'created', 'published']

    def post(self, request, format=None):
        serializer = SequenceSerializer(data=request.data,
                                        context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
