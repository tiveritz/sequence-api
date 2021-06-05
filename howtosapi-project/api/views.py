from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import status

from api.models import HowTo, HowToUriId
from api.serializers import HowToSerializer, HowToDetailSerializer


class APIRoot(APIView):
    def get(self, request):
        return Response({
            'statistics' : reverse('statistics', request = request),
            'howtos' : reverse('how-to-list', request = request),
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
        steps_count = 34
        supersteps_count = 34
        substeps_count = 34
        
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
    
    def post(self, request, format=None):
        serializer = HowToSerializer(data = request.data, context={'request': request})
        if serializer.is_valid():
            print('view was called')
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

class HowToDetailView(APIView):
    """
    View to How To with it's content
    """
    def get(self, request, pk):
        how_to = HowTo.objects.get(pk = pk)
        serializer = HowToDetailSerializer(how_to)
        return Response(serializer.data)
