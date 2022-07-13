from django.conf import settings

from rest_framework.response import Response
from rest_framework.views import APIView

from api.base.choices import StepChoices
from api.models.content import Explanation, Image
from api.models.sequence import Sequence
from api.models.step import (
    Step,
    LinkedStep)


class StatisticView(APIView):
    def get(self, request):
        sequence_count = Sequence.objects.count()
        steps_count = Step.objects.exclude(type=StepChoices.SEQUENCE).count()
        images_count = Image.objects.count()

        linked_step_uuids = LinkedStep.objects.values_list(
            'super__uuid', flat=True)
        sub_count = Step.objects.exclude(uuid__in=linked_step_uuids).count()
        super_count = linked_step_uuids.count()

        text_modules_count = Explanation.objects.filter(type='text').count()
        code_modules_count = Explanation.objects.filter(type='code').count()
        modules_count = images_count + text_modules_count + code_modules_count

        return Response({'version': settings.VERSION,
                         'sequences': sequence_count,
                         'steps': steps_count,
                         'super': super_count,
                         'sub': sub_count,
                         'modules': modules_count,
                         'text_modules': text_modules_count,
                         'code_modules': code_modules_count,
                         'images': images_count,
                         })
