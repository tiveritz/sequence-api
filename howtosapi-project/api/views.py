from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from api.uri_id_generator import generate
from api.models import HowTo, HowToUriId
from api.serializers import HowToSerializer, HowToDetailSerializer


class StatisticView(APIView):
    def get(self, request, format = None):
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


class HowToViewSet(viewsets.ModelViewSet):
    queryset = HowTo.objects.all().order_by('-updated')
    serializer_class = HowToSerializer
    detail_serializer_class = HowToDetailSerializer

    def get_serializer_class(self):
        """
        Overrides the default method behaviour of retrieve (detail view)
        by returning the detail serializer class
        """
        if self.action =='retrieve':
            return self.detail_serializer_class
        return super(HowToViewSet, self).get_serializer_class()

    def perform_create(self, serializer):
        '''
        Overrides automatic creation in order to automatically generate
        an uri id
        '''
        how_to = serializer.save()
        uri_id = generate(how_to.id)
        how_to_uri_id = HowToUriId(
            uri_id = uri_id,
            how_to_id = how_to
        )
        how_to_uri_id.save()
