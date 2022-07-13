from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveDestroyAPIView
from rest_framework.response import Response

from api.filters import SequenceSearchFilter, SequenceOrderingFilter
from api.models.sequence import Sequence
from api.models.step import Step
from api.serializers.sequence_serializers import (SequenceSerializer,
                                                  SequencesSerializer)
from core.pagination import ListPagination


class SequenceView(RetrieveDestroyAPIView):
    def get(self, request, uuid):
        sequence = Sequence.objects.get(step__uuid=uuid)
        serializer = SequenceSerializer(sequence,
                                        context={'request': request})
        return Response(serializer.data)

    def patch(self, request, uuid):
        sequence = Sequence.objects.get(step__uuid=uuid)

        context = {'request': request}
        serializer = SequenceSerializer(sequence,
                                        data=request.data,
                                        context=context,
                                        partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

    def delete(self, request, uuid):
        Sequence.objects.get(step__uuid=uuid).delete()
        Step.objects.get(uuid=uuid).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class SequenceListView(ListCreateAPIView):
    queryset = Sequence.objects.all().order_by('-updated')
    serializer_class = SequencesSerializer
    pagination_class = ListPagination
    filter_backends = [SequenceSearchFilter, SequenceOrderingFilter]
    search_fields = ['title']
    ordering_fields = ['title', 'updated', 'created', 'published']

    def post(self, request, format=None):
        serializer = SequencesSerializer(data=request.data,
                                         context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
