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

from api.base.choices import StepChoices
from api.models import Step, LinkedStep
from api.serializers.step_serializers import (LinkStepSerializer,
                                              StepDetailSerializer,
                                              StepSerializer)


class StepView(RetrieveDestroyAPIView):
    serializer_class = StepDetailSerializer

    def get(self, request, uuid):
        step = Step.objects.get(uuid=uuid)
        serializer = StepDetailSerializer(step, context={'request': request})
        return Response(serializer.data)

    def patch(self, request, uuid):
        step = Step.objects.get(uuid=uuid)

        context = {'request': request}
        serializer = StepSerializer(step,
                                    data=request.data,
                                    context=context,
                                    partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

    def delete(self, request, uuid):
        Step.objects.get(uuid=uuid).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class StepListView(ListCreateAPIView):
    queryset = Step.objects.exclude(type=StepChoices.SEQUENCE) \
                           .order_by('-updated')
    serializer_class = StepSerializer
    pagination_class = ListPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title']
    ordering_fields = ['title', 'created', 'updated']

    def post(self, request):
        serializer = StepSerializer(data=request.data,
                                    context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)


class StepLinkableListView(ListAPIView):
    serializer_class = StepSerializer
    pagination_class = ListPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title']
    ordering_fields = ['title', 'created', 'updated']

    def get_queryset(self):
        super = Step.objects.get(uuid=self.kwargs['uuid'])
        parent_pks = super.get_parent_pks()
        linked = super.linked
        children = [li.pk for li in linked]
        excluded_pks = children + [super.pk] + parent_pks

        return Step.objects.exclude(pk__in=excluded_pks).order_by('-updated')


class LinkStepView(CreateAPIView):
    def post(self, request, uuid):
        context = {'uuid': uuid}
        serializer = LinkStepSerializer(data=request.data, context=context)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class LinkedStepDeleteView(DestroyAPIView):
    def delete(self, request, uuid):
        linked_step = LinkedStep.objects.get(super__uuid=uuid,
                                             sub__uuid=request.data['sub'])
        max_pos = LinkedStep.objects.filter(super__uuid=uuid) \
                                    .aggregate(Max('pos'))['pos__max']

        LinkedStep.objects.filter(super__uuid=uuid) \
                          .filter(pos__gt=linked_step.pos) \
                          .filter(pos__lte=max_pos) \
                          .update(pos=F('pos') - 1)

        linked_step.delete()

        if max_pos == 0:
            Step.objects.filter(uuid=uuid).update(type=StepChoices.STEP)

        return Response(status=status.HTTP_204_NO_CONTENT)


class LinkedStepOrderView(ListAPIView):
    def post(self, request, uuid):
        from_index = request.data['from_index']
        to_index = request.data['to_index']
        linked_step = LinkedStep.objects.get(super__uuid=uuid, pos=from_index)

        if from_index < to_index:  # Move down
            LinkedStep.objects.filter(super__uuid=uuid) \
                .filter(pos__gt=from_index) \
                .filter(pos__lte=to_index) \
                .update(pos=F('pos') - 1)

        if from_index > to_index:  # Move up
            LinkedStep.objects.filter(super__uuid=uuid) \
                .filter(pos__lt=from_index) \
                .filter(pos__gte=to_index) \
                .update(pos=F('pos') + 1)

        linked_step.pos = to_index
        linked_step.save()

        return Response(status=status.HTTP_200_OK)


class StepUsageView(ListAPIView):
    pass
