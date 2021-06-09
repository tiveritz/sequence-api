from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import status

from api.models import HowTo, Step
from api.serializers import HowToSerializer, HowToDetailSerializer, StepSerializer, StepDetailSerializer, HowToStepSerializer


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
        supersteps_count = 0
        substeps_count = 0
        
        return Response({
            'how_tos' : how_tos_count,
            'steps' : steps_count,
            'supersteps' : supersteps_count,
            'substeps' : substeps_count,
            })

class HowToListView(APIView):
    """
    View to How To's
    """
    def get(self, request):
        how_tos = HowTo.objects.all().order_by('-updated')
        serializer = HowToSerializer(
            how_tos,
            many = True,
            context = {'request' : request}
            )
        return Response(serializer.data)
    
    def post(self, request, format = None):
        serializer = HowToSerializer(data = request.data, context = {'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

class HowToDetailView(APIView):
    """
    View to How To with it's content
    """
    def get(self, request, uri_id):
        how_to = HowTo.objects.get(howtouriid__uri_id = uri_id)
        serializer = HowToDetailSerializer(how_to, context = {'request' : request})
        return Response(serializer.data)
    
    def patch(self, request, uri_id):
        how_to = HowTo.objects.get(howtouriid__uri_id = uri_id)
        serializer = HowToDetailSerializer(how_to, data = request.data, partial = True, context = {'request' : request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_200_OK)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

class HowToStepView(APIView):
    """
    View to Steps of a How To
    """
    def post(self, request, uri_id, format = None):
        data = request.data
        data['how_to_uri_id'] = uri_id
        serializer = HowToStepSerializer(data = data)
        if serializer.is_valid():
            serializer.save()
            return Response(status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

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
        serializer = StepSerializer(data = request.data, context = {'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

class StepDetailView(APIView):
    """
    View to Step with it's content
    """
    def get(self, request, uri_id):
        step = Step.objects.get(stepuriid__uri_id = uri_id)
        serializer = StepDetailSerializer(step)
        return Response(serializer.data)
    
    def patch(self, request, uri_id):
        step = Step.objects.get(stepuriid__uri_id = uri_id)
        serializer = StepDetailSerializer(step, data = request.data, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_200_OK)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)