from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import Sequence, Step, SuperStep, DecisionStep, Explanation, Image


class StatisticView(APIView):
    """
    View to statistical data of the content
    """

    def get(self, request):
        """
        Return statisitcal data
        """
        sequence_count = Sequence.objects.count()
        steps_count = Step.objects.count()
        images_count = Image.objects.count()

        superstep_ids = SuperStep.objects.values_list(
            'super__api_id', flat=True)
        substeps_count = Step.objects.exclude(api_id__in=superstep_ids).count()
        supersteps_count = superstep_ids.count()

        decision_ids = DecisionStep.objects.values_list(
            'super__api_id', flat=True)
        decisions_count = decision_ids.count()

        text_modules_count = Explanation.objects.filter(type='text').count()
        code_modules_count = Explanation.objects.filter(type='code').count()
        modules_count = images_count + text_modules_count + code_modules_count

        return Response({'version': settings.VERSION,
                         'sequences': sequence_count,
                         'steps': steps_count,
                         'supersteps': supersteps_count,
                         'substeps': substeps_count,
                         'decisions': decisions_count,
                         'modules': modules_count,
                         'text_modules': text_modules_count,
                         'code_modules': code_modules_count,
                         'images': images_count,
                         })
