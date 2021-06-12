from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import status

from api.models import HowTo, Step, HowToStep, HowToUriId, StepUriId, Super
from api.serializers import (HowToSerializer,
                             HowToDetailSerializer,
                             HowToStepSerializer,
                             StepSerializer,
                             StepSimpleSerializer,
                             StepDetailSerializer,
                             SubstepSerializer)


class APIRoot(APIView):
    def get(self, request):
        return Response({
            'statistics' : reverse('statistics', request = request),
            'howtos' : reverse('how-to-list', request = request),
            'steps' : reverse('step-list', request = request),
        })

class StatisticView(APIView):
    """
    View to statistical data of the content
    """
    def get(self, request):
        """
        Return statisitcal data
        """
        how_tos_count = HowTo.objects.count()
        steps_count = Step.objects.count()

        superstep_ids = Super.objects.values_list('super_id__id', flat = True)
        substeps_count = Step.objects.exclude(id__in = superstep_ids).count()

        supersteps_count = superstep_ids.count()
        
        return Response({'how_tos' : how_tos_count,
                         'steps' : steps_count,
                         'supersteps' : supersteps_count,
                         'substeps' : substeps_count,})

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
                        status = status.HTTP_400_BAD_REQUEST)

class SubstepView(APIView):
    """
    View to Substeps
    """
    def get(self, request, uri_id):
        super = Step.objects.get(stepuriid__uri_id = uri_id)
        steps = super.substeps
        serializer = StepSimpleSerializer(steps,
                                          many = True,
                                          context = {'request' : request})
        return Response(serializer.data)

    def post(self, request, uri_id, format = None):
        data = request.data
        data['super_uri_id'] = uri_id
        serializer = SubstepSerializer(data = data)
        if serializer.is_valid():
            serializer.save()
            return Response(status = status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status = status.HTTP_400_BAD_REQUEST)

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
        steps = Step.objects.exclude(id__in = forbidden_steps)


        serializer = StepSimpleSerializer(steps,
                                          many = True,
                                          context = {'request' : request})
        return Response(serializer.data,
                        status = status.HTTP_200_OK)

class SuperDetailView(APIView):
    """
    View to Steps of a How To
    """
    def delete(self, request, uri_id, step_uri_id):
        super = StepUriId.objects.get(uri_id = uri_id)
        step = StepUriId.objects.get(uri_id = step_uri_id)
        Super.objects.filter(super_id = super.id,
                             step_id = step.id).delete()
        return Response(status = status.HTTP_204_NO_CONTENT)

class StepListView(APIView):
    """
    View to Steps
    """
    def get(self, request):
        steps = Step.objects.all().order_by('-updated')
        serializer = StepSerializer(
            steps,
            many = True,
            context = {'request' : request}
            )
        return Response(serializer.data)

    def post(self, request, format = None):
        serializer = StepSerializer(data = request.data,
                                    context = {'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status = status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status = status.HTTP_400_BAD_REQUEST)

class StepDetailView(APIView):
    """
    View to Step with it's content
    """
    def get(self, request, uri_id):
        step = Step.objects.get(stepuriid__uri_id = uri_id)
        serializer = StepDetailSerializer(step,
                                          context = {'request': request})
        return Response(serializer.data)
    
    def patch(self, request, uri_id):
        step = Step.objects.get(stepuriid__uri_id = uri_id)
        serializer = StepDetailSerializer(step,
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
        Step.objects.get(stepuriid__uri_id = uri_id).delete()
        return Response(status = status.HTTP_204_NO_CONTENT)

class StepLinkableView(APIView):
    """
    View to Steps that can be linked to a How To
    """
    def get(self, request, uri_id):
        # Can not link itself
        self_id = Step.objects.get(stepuriid__uri_id = uri_id).id

        # Can not link a Substep of this Step
        forbidden_substeps = Step.objects.get(stepuriid__uri_id = uri_id).substeps
        
        
        steps = Step.objects.exclude(id = self_id).exclude(id__in = forbidden_substeps)

        serializer = StepSimpleSerializer(steps,
                                          many = True,
                                          context = {'request' : request})
        return Response(serializer.data,
                        status = status.HTTP_200_OK)