from core.pagination import ListPagination
from django.db.models import F, Max

from rest_framework import status
from rest_framework.generics import (CreateAPIView,
                                     DestroyAPIView,
                                     ListAPIView,
                                     ListCreateAPIView,
                                     RetrieveDestroyAPIView)
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response

from api.models import Step, SuperStep
from api.serializers.step_serializers import (SubstepAddSerializer,
                                              StepSerializer)


class StepView(RetrieveDestroyAPIView):
    def get(self, request, uuid):
        step = Step.objects.get(uuid=uuid)
        serializer = StepSerializer(step, context={'request': request})
        return Response(serializer.data)

    def patch(self, request, uuid):
        step = Step.objects.get(uuid=uuid)

        context = {'request': request}
        serializer = StepSerializer(step, data=request.data, context=context, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

    def delete(self, request, uuid):
        Step.objects.get(uuid=uuid).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class StepListView(ListCreateAPIView):
    queryset = Step.objects.all().order_by('-updated')
    serializer_class = StepSerializer
    pagination_class = ListPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title']
    ordering_fields = ['title', 'created', 'updated']

    def post(self, request):
        serializer = StepSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)


class StepLinkableListView(ListAPIView):
    pass


class SubstepAddView(CreateAPIView):
    def post(self, request, uuid):
        context = {'uuid': uuid}
        serializer = SubstepAddSerializer(data=request.data, context=context)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class SubstepDeleteView(DestroyAPIView):
    def delete(self, request, uuid):
        superstep = SuperStep.objects.get(super__uuid=uuid, sub__uuid=request.data['sub'])
        max_pos = SuperStep.objects.filter(super__uuid=uuid).aggregate(Max('pos'))['pos__max']

        SuperStep.objects.filter(super__uuid=uuid) \
                         .filter(pos__gt=superstep.pos) \
                         .filter(pos__lte=max_pos) \
                         .update(pos=F('pos') - 1)

        superstep.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class SubstepOrderView(ListAPIView):
    def post(self, request, uuid):
        from_index = request.data['from_index']
        to_index = request.data['to_index']
        superstep = SuperStep.objects.get(super__uuid=uuid, pos=from_index)

        if from_index < to_index:  # Move down
            SuperStep.objects.filter(super__uuid=uuid) \
                .filter(pos__gt=from_index) \
                .filter(pos__lte=to_index) \
                .update(pos=F('pos') - 1)

        if from_index > to_index:  # Move up
            SuperStep.objects.filter(super__uuid=uuid) \
                .filter(pos__lt=from_index) \
                .filter(pos__gte=to_index) \
                .update(pos=F('pos') + 1)

        superstep.pos = to_index
        superstep.save()

        return Response(status=status.HTTP_200_OK)


class StepUsageView(ListAPIView):
    pass
