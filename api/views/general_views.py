from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import HowTo, Step, SuperStep, Explanation, Image


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
        images_count = Image.objects.count()

        superstep_ids = SuperStep.objects.values_list(
            'super__uri_id', flat=True)
        substeps_count = Step.objects.exclude(uri_id__in=superstep_ids).count()
        supersteps_count = superstep_ids.count()

        text_modules_count = Explanation.objects.filter(type='text').count()
        code_modules_count = Explanation.objects.filter(type='code').count()
        modules_count = images_count + text_modules_count + code_modules_count

        return Response({'version': settings.VERSION,
                         'how_tos': how_tos_count,
                         'steps': steps_count,
                         'supersteps': supersteps_count,
                         'substeps': substeps_count,
                         'modules': modules_count,
                         'text_modules': text_modules_count,
                         'code_modules': code_modules_count,
                         'images': images_count,
                         })
