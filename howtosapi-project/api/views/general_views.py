from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import HowTo, Super, Step, Explanation


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

        explanations_count = Explanation.objects.count()
        text_modules_count = Explanation.objects.filter(type = 'text').count()
        code_modules_count = Explanation.objects.filter(type = 'code').count()
        
        return Response({'how_tos' : how_tos_count,
                         'steps' : steps_count,
                         'supersteps' : supersteps_count,
                         'substeps' : substeps_count,
                         'explanations' : explanations_count,
                         'text_modules' : text_modules_count,
                         'code_modules' : code_modules_count,
                         })
