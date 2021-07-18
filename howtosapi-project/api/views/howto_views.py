from django.db.models import F
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import HowTo, Step, HowToStep, HowToUriId, StepUriId, HowToStep
from ..serializers.howto_serializers import (HowToSerializer,
                                             HowToDetailSerializer,
                                             HowToStepSerializer,
                                             StepSimpleSerializer)


class HowToListView(APIView):
    """
    View to How To's
    """
    def get(self, request):
        how_tos = HowTo.objects.all().order_by('-updated')
        serializer = HowToSerializer(how_tos,
                                     many = True,
                                     context = {'request' : request})
        return Response(serializer.data)
    
    def post(self, request, format = None):
        serializer = HowToSerializer(data = request.data,
                                     context = {'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status = status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status = status.HTTP_400_BAD_REQUEST)


class HowToDetailView(APIView):
    """
    View to How To with it's content
    """
    def get(self, request, uri_id):
        how_to = HowTo.objects.get(howtouriid__uri_id = uri_id)
 
        serializer = HowToDetailSerializer(how_to,
                                           context = {'request' : request})
        return Response(serializer.data)
    
    def patch(self, request, uri_id):
        how_to = HowTo.objects.get(howtouriid__uri_id = uri_id)
        serializer = HowToDetailSerializer(how_to,
                                           data = request.data,
                                           partial = True,
                                           context = {'request' : request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status = status.HTTP_200_OK)
        return Response(serializer.errors,
                        status = status.HTTP_400_BAD_REQUEST)

    def delete(self, request, uri_id):
        HowTo.objects.get(howtouriid__uri_id = uri_id).delete()
        return Response(status = status.HTTP_204_NO_CONTENT)


class HowToStepView(APIView):
    """
    View to Steps of a How To
    """
    def get(self, request, uri_id):
        how_to = HowTo.objects.get(howtouriid__uri_id = uri_id)
        steps = how_to.steps
        serializer = StepSimpleSerializer(steps,
                                          many = True,
                                          context = {'request' : request})
        return Response(serializer.data)

    def post(self, request, uri_id, format = None):
        data = request.data
        data['how_to_uri_id'] = uri_id
        serializer = HowToStepSerializer(data = data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(status = status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status = status.HTTP_403_FORBIDDEN)
    
    def patch(self, request, uri_id):
        data = request.data
        method = data['method']
        how_to = HowTo.objects.get(howtouriid__uri_id = uri_id)

        if method == 'order':
            old_index = data['old_index']
            new_index = data['new_index']
            how_to_step = HowToStep.objects.get(how_to_id = how_to.id, pos = old_index)

            if old_index < new_index: # Move down
                HowToStep.objects.filter(how_to_id = how_to.id) \
                                 .filter(pos__gt = old_index)   \
                                 .filter(pos__lte = new_index)  \
                                 .update(pos = F('pos') - 1)
                how_to_step.pos = new_index
                how_to_step.save()

            if old_index > new_index: # Move up
                HowToStep.objects.filter(how_to_id = how_to.id) \
                                 .filter(pos__lt = old_index)   \
                                 .filter(pos__gte = new_index)  \
                                 .update(pos = F('pos') + 1)
                how_to_step.pos = new_index
                how_to_step.save()

            return Response(status = status.HTTP_200_OK)

        if method == 'delete':
            from django.db.models import Max

            step_uri_id = data['uri_id']

            step = Step.objects.get(stepuriid__uri_id = step_uri_id)
            delete = HowToStep.objects.get(how_to_id = how_to, step_id = step)
            max_pos = HowToStep.objects.filter(how_to_id = how_to).aggregate(Max('pos'))['pos__max']
            pos = delete.pos

            delete.delete()

            if pos != max_pos: # Move all following steps up
                HowToStep.objects.filter(how_to_id = how_to.id) \
                                 .filter(pos__gt = pos)   \
                                 .filter(pos__lte = max_pos)  \
                                 .update(pos = F('pos') - 1)

            return Response(status = status.HTTP_200_OK)
        return Response(status = status.HTTP_400_BAD_REQUEST)


class HowToStepDetailView(APIView):
    """
    View to Steps of a How To
    """
    def delete(self, request, uri_id, step_uri_id):
        how_to = HowToUriId.objects.get(uri_id = uri_id)
        step = StepUriId.objects.get(uri_id = step_uri_id)
        HowToStep.objects.filter(how_to_id = how_to.id,
                                 step_id = step.id).delete()
        return Response(status = status.HTTP_204_NO_CONTENT)


class HowToLinkableView(APIView):
    """
    View to Steps that can be linked to a How To
    """
    def get(self, request, uri_id):
        # Can not be linked to this How To already
        forbidden_steps = HowTo.objects.get(howtouriid__uri_id = uri_id).steps
        steps = Step.objects.exclude(id__in = forbidden_steps).order_by('-updated')


        serializer = StepSimpleSerializer(steps,
                                          many = True,
                                          context = {'request' : request})
        return Response(serializer.data,
                        status = status.HTTP_200_OK)
