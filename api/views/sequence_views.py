import copy
import uuid

from django.db.models import F
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from django.utils import timezone
from core.pagination import ListPagination

from ..models import (Sequence, Step, SequenceStep, SequenceStep, SequenceGuide,
                      SequenceGuideStep)

from ..serializers.sequence_serializers import (SequenceSerializer,
                                             SequenceDetailSerializer,
                                             SequenceStepSerializer,
                                             StepSimpleSerializer,)


class SequenceListView(ListAPIView):
    """
    View to Sequences
    """
    queryset = Sequence.objects.all().order_by('-updated')
    serializer_class = SequenceSerializer
    pagination_class = ListPagination

    def post(self, request, format=None):
        serializer = SequenceSerializer(data=request.data,
                                     context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class SequenceDetailView(APIView):
    """
    View to Sequence with it's content
    """

    def get(self, request, api_id):
        try:
            sequence = Sequence.objects.get(api_id=api_id)
        except Sequence.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = SequenceDetailSerializer(sequence,
                                           context={'request': request})
        return Response(serializer.data)

    def patch(self, request, api_id):
        sequence = Sequence.objects.get(api_id=api_id)
        serializer = SequenceDetailSerializer(sequence,
                                           data=request.data,
                                           partial=True,
                                           context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_200_OK)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, api_id):
        Sequence.objects.get(api_id=api_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SequenceStepView(APIView):
    """
    View to Steps of a Sequence
    """

    def get(self, request, api_id):
        sequence_steps = Sequence.objects.get(api_id=api_id).steps
        serializer = StepSimpleSerializer(sequence_steps,
                                          many=True,
                                          context={'request': request})
        return Response(serializer.data)

    def post(self, request, api_id, format=None):
        data = request.data.copy()  # TODO: only pytest complains about that
        data['sequence_api_id'] = api_id
        serializer = SequenceStepSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_403_FORBIDDEN)

    def patch(self, request, api_id):
        data = request.data.copy()
        method = data['method']
        sequence = Sequence.objects.get(api_id=api_id)

        if method == 'order':
            old_index = data['old_index']
            new_index = data['new_index']
            sequence_step = SequenceStep.objects.get(sequence=sequence, pos=old_index)

            if old_index < new_index:  # Move down
                SequenceStep.objects.filter(sequence=sequence) \
                                 .filter(pos__gt=old_index)   \
                                 .filter(pos__lte=new_index)  \
                                 .update(pos=F('pos') - 1)
                sequence_step.pos = new_index
                sequence_step.save()

            if old_index > new_index:  # Move up
                SequenceStep.objects.filter(sequence=sequence) \
                                 .filter(pos__lt=old_index)   \
                                 .filter(pos__gte=new_index)  \
                                 .update(pos=F('pos') + 1)
                sequence_step.pos = new_index
                sequence_step.save()

            return Response(status=status.HTTP_200_OK)

        if method == 'delete':
            from django.db.models import Max

            step_api_id = data['api_id']

            step = Step.objects.get(api_id=step_api_id)
            delete = SequenceStep.objects.get(sequence=sequence, step=step)
            max_pos = SequenceStep.objects.filter(sequence=sequence) \
                .aggregate(Max('pos'))['pos__max']
            pos = delete.pos

            delete.delete()

            if pos != max_pos:  # Move all following steps up
                SequenceStep.objects.filter(sequence=sequence) \
                                 .filter(pos__gt=pos)   \
                                 .filter(pos__lte=max_pos)  \
                                 .update(pos=F('pos') - 1)

            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class SequenceStepDetailView(APIView):
    """
    View to Steps of a Sequence
    """

    def delete(self, request, api_id, step_api_id):
        sequence = Sequence.objects.get(api_id=api_id)
        step = Step.objects.get(api_id=step_api_id)
        SequenceStep.objects.filter(sequence=sequence,
                                 step=step).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SequenceLinkableView(APIView):
    """
    View to Steps that can be linked to a Sequence
    """

    def get(self, request, api_id):
        # Can not be linked to this Sequence already
        forbidden_steps = Sequence.objects.get(api_id=api_id).steps
        forbidden_api_ids = [step.api_id for step in forbidden_steps]
        steps = Step.objects.exclude(
            api_id__in=forbidden_api_ids).order_by('-updated')

        serializer = StepSimpleSerializer(steps,
                                          many=True,
                                          context={'request': request})
        return Response(serializer.data,
                        status=status.HTTP_200_OK)


class SequencePublishView(APIView):
    """
    View to Publish a Sequence
    """

    def _render_content(self, modules):
        if modules:
            rendered = ''
            for module in modules:
                if module.type == 'text':
                    before = '<pre class="module-text">\n'
                    after = '</pre>\n'
                    content = before + module.content + after
                    rendered += content

                elif module.type == 'code':
                    before = '<pre class="module-code">\n'
                    after = '</pre>\n'
                    content = before + module.content + after
                    rendered += content

                elif module.type == 'image':
                    img = '<img class="module-image" src="[[img|{}]]" alt="{}">\n'.format(
                        module.api_id, module.caption
                    )
                    rendered += img
            return rendered
        return ''

    def _recursive_stepdict(self, step, level, number):
        stepdict = {}
        number[level] += 1

        stepdict[step.api_id] = {
            'ref_api_id': uuid.uuid4(),
            'number': '.'.join([str(pos) for pos in number]),
            'title': step.title,
            'current': False,
            'level': level,
        }

        if step.substeps:
            level += 1
            new_number = number[:]
            new_number.append(0)
            for step in step.substeps:
                substepdict = self._recursive_stepdict(step, level, new_number)
                stepdict = {**stepdict, **substepdict}
        return stepdict

    def _recursive_guide_step(self, guide_sequence, step):

        rendered_content = self._render_content(step.modules)

        SequenceGuideStep.objects.create(
            api_id='a',
            ref_api_id='b',
            sequence=guide_sequence,
            sequence_title=guide_sequence.title,
            title=step.title,
            steps='c',
            decisions='c',
            first='e',
            first_ref='f',
            previous='g',
            previous_ref='h',
            next='i',
            next_ref='j',
            content=rendered_content,
        )

        if step.substeps:
            for step in step.substeps:
                self._recursive_guide_step(
                    guide_sequence, step)

    def asdf_post(self, request, api_id):
        spaces = request.data['spaces']

        spaces_dict = {
            'test': 'TST',
            'preview': 'PRV',
            'public': 'PBL',
            'private': 'PRV',
        }

        # Delete previous published data
        for space in spaces:
            try:
                SequenceGuide.objects.get(sequence_api_id=api_id,
                                       space=spaces_dict[space]).delete()
            except SequenceGuide.DoesNotExist:
                pass  # The SequenceGuide was not published before. Nothing to do

        # Get Sequence
        sequence = Sequence.objects.get(api_id=api_id)

        # Get Sequence Steps
        steps = sequence.steps

        # Generate stepdict
        stepdict = {}
        number = [0]
        for step in steps:
            stepdict = {**stepdict, **self._recursive_stepdict(step, 0, number)}
        steplist = list(stepdict.keys())

        json_stepdict = {}
        step_pos = 0
        for step in steplist:
            step = {
                step_pos: {
                    'api_id': step,
                    'ref_api_id': stepdict[step]['ref_api_id'],
                    'number': stepdict[step]['number'],
                    'title': stepdict[step]['title'],
                    'current': stepdict[step]['current'],
                    'level': stepdict[step]['level'],
                }
            }
            json_stepdict = {**json_stepdict, **step}
            step_pos += 1

        # Write SequenceGuide
        for space in spaces:
            guide_sequence = SequenceGuide.objects.create(
                sequence_api_id=sequence.api_id,
                space=spaces_dict[space],
                title=sequence.title,
                first=steps[0].api_id,
                first_ref=stepdict[steps[0].api_id]['ref_api_id'],
                steps=json_stepdict,
            )

            # Write SequenceGuideStep
            for step in steps:
                self._recursive_guide_step(
                    guide_sequence, step, stepdict, steplist)

        # Save Successful publish to Sequence
        sequence.is_published = True
        sequence.publish_date = timezone.now()
        sequence.save()

        payload = {
            'is_published': sequence.is_published,
            'publish_date': sequence.publish_date,
        }

        return Response(payload,
                        status=status.HTTP_200_OK)

    def _recursive_toc(self, steps):
        # toc = Table of Content
        toc = []
        for step in steps:
            stepdict = {
                'type': 'decision' if step.is_decision else 'step',
                'title': step.title,
            }
            if step.is_decision:
                stepdict['decisions'] = self._recursive_toc(step.decisionsteps)
            else:
                stepdict['substeps'] = self._recursive_toc(step.substeps)

            toc.append(stepdict)
        return toc

    def post(self, request, api_id):
        spaces = request.data['spaces']

        spaces_dict = {
            'test': 'TST',
            'preview': 'PRV',
            'public': 'PBL',
            'private': 'PRV',
        }

        # Delete previous published data
        for space in spaces:
            try:
                SequenceGuide.objects.get(sequence_api_id=api_id,
                                       space=spaces_dict[space]).delete()
            except SequenceGuide.DoesNotExist:
                pass  # The SequenceGuide was not published before. Nothing to do

        # Get Sequence
        sequence = Sequence.objects.get(api_id=api_id)

        # Get Sequence Steps
        steps = sequence.steps

        # Get table of content
        toc = self._recursive_toc(sequence.steps)


        # Write SequenceGuide
        for space in spaces:
            guide_sequence = SequenceGuide.objects.create(
                sequence_api_id=sequence.api_id,
                space=spaces_dict[space],
                title=sequence.title,
                first=steps[0].api_id,
                first_ref='a',
                steps='steps',
            )

            # Write SequenceGuideStep
            for step in steps:
                self._recursive_guide_step(
                    guide_sequence, step)

        # Save Successful publish to Sequence
        sequence.is_published = True
        sequence.publish_date = timezone.now()
        sequence.save()

        payload = {
            'is_published': sequence.is_published,
            'publish_date': sequence.publish_date,
        }

        return Response(payload,
                        status=status.HTTP_200_OK)
