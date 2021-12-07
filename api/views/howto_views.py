import copy
from django.db.models import F
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from ..functions.uri_id import generate_uri_id

from ..models import (HowTo, Step, HowToStep, HowToStep, HowToGuide,
                      HowToGuideStep)

from ..serializers.howto_serializers import (HowToSerializer,
                                             HowToDetailSerializer,
                                             HowToStepSerializer,
                                             StepSimpleSerializer,)


class HowToListView(APIView):
    """
    View to How To's
    """

    def get(self, request):
        how_tos = HowTo.objects.all().order_by('-updated')
        serializer = HowToSerializer(how_tos,
                                     many=True,
                                     context={'request': request})
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = HowToSerializer(data=request.data,
                                     context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class HowToDetailView(APIView):
    """
    View to How To with it's content
    """

    def get(self, request, uri_id):
        try:
            how_to = HowTo.objects.get(uri_id=uri_id)
        except HowTo.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = HowToDetailSerializer(how_to,
                                           context={'request': request})
        return Response(serializer.data)

    def patch(self, request, uri_id):
        how_to = HowTo.objects.get(uri_id=uri_id)
        serializer = HowToDetailSerializer(how_to,
                                           data=request.data,
                                           partial=True,
                                           context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_200_OK)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, uri_id):
        HowTo.objects.get(uri_id=uri_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class HowToStepView(APIView):
    """
    View to Steps of a How To
    """

    def get(self, request, uri_id):
        how_to_steps = HowTo.objects.get(uri_id=uri_id).steps
        serializer = StepSimpleSerializer(how_to_steps,
                                          many=True,
                                          context={'request': request})
        return Response(serializer.data)

    def post(self, request, uri_id, format=None):
        data = request.data.copy()  # TODO: only pytest complains about that
        data['how_to_uri_id'] = uri_id
        serializer = HowToStepSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_403_FORBIDDEN)

    def patch(self, request, uri_id):
        data = request.data.copy()
        method = data['method']
        how_to = HowTo.objects.get(uri_id=uri_id)

        if method == 'order':
            old_index = data['old_index']
            new_index = data['new_index']
            how_to_step = HowToStep.objects.get(how_to=how_to, pos=old_index)

            if old_index < new_index:  # Move down
                HowToStep.objects.filter(how_to=how_to) \
                                 .filter(pos__gt=old_index)   \
                                 .filter(pos__lte=new_index)  \
                                 .update(pos=F('pos') - 1)
                how_to_step.pos = new_index
                how_to_step.save()

            if old_index > new_index:  # Move up
                HowToStep.objects.filter(how_to=how_to) \
                                 .filter(pos__lt=old_index)   \
                                 .filter(pos__gte=new_index)  \
                                 .update(pos=F('pos') + 1)
                how_to_step.pos = new_index
                how_to_step.save()

            return Response(status=status.HTTP_200_OK)

        if method == 'delete':
            from django.db.models import Max

            step_uri_id = data['uri_id']

            step = Step.objects.get(uri_id=step_uri_id)
            delete = HowToStep.objects.get(how_to=how_to, step=step)
            max_pos = HowToStep.objects.filter(how_to=how_to) \
                .aggregate(Max('pos'))['pos__max']
            pos = delete.pos

            delete.delete()

            if pos != max_pos:  # Move all following steps up
                HowToStep.objects.filter(how_to=how_to) \
                                 .filter(pos__gt=pos)   \
                                 .filter(pos__lte=max_pos)  \
                                 .update(pos=F('pos') - 1)

            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class HowToStepDetailView(APIView):
    """
    View to Steps of a How To
    """

    def delete(self, request, uri_id, step_uri_id):
        how_to = HowTo.objects.get(uri_id=uri_id)
        step = Step.objects.get(uri_id=step_uri_id)
        HowToStep.objects.filter(how_to=how_to,
                                 step=step).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class HowToLinkableView(APIView):
    """
    View to Steps that can be linked to a How To
    """

    def get(self, request, uri_id):
        # Can not be linked to this How To already
        forbidden_steps = HowTo.objects.get(uri_id=uri_id).steps
        forbidden_uri_ids = [step.uri_id for step in forbidden_steps]
        steps = Step.objects.exclude(
            uri_id__in=forbidden_uri_ids).order_by('-updated')

        serializer = StepSimpleSerializer(steps,
                                          many=True,
                                          context={'request': request})
        return Response(serializer.data,
                        status=status.HTTP_200_OK)


class HowToPublishView(APIView):
    """
    View to Publish a How To
    """

    def render_content(self, modules):
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
                        module.uri_id, module.caption
                    )
                    rendered += img
            return rendered
        return ''

    def recursive_stepdict(self, step, level, number):
        stepdict = {}
        number[level] += 1

        stepdict[step.uri_id] = {
            'ref_id': generate_uri_id(),
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
                substepdict = self.recursive_stepdict(step, level, new_number)
                stepdict = {**stepdict, **substepdict}
        return stepdict

    def recursive_guide_step(self, guide_howto, step, stepdict, steplist):
        stepdict_current = copy.deepcopy(stepdict)
        stepdict_current[step.uri_id]['current'] = True
        pos = steplist.index(step.uri_id)

        json_stepdict = {}
        step_pos = 0
        for uri_id in steplist:
            step_current = {
                step_pos: {
                    'uri_id': uri_id,
                    'ref_id': stepdict_current[uri_id]['ref_id'],
                    'number': stepdict_current[uri_id]['number'],
                    'title': stepdict_current[uri_id]['title'],
                    'current': stepdict_current[uri_id]['current'],
                    'level': stepdict_current[uri_id]['level'],
                }
            }
            json_stepdict = {**json_stepdict, **step_current}
            step_pos += 1

        uri_id = json_stepdict[pos]['uri_id']
        ref_id = json_stepdict[pos]['ref_id']

        first = json_stepdict[0]['uri_id']
        first_ref = json_stepdict[0]['ref_id']

        if pos > 0:
            previous = json_stepdict[pos-1]['uri_id']
            previous_ref = json_stepdict[pos-1]['ref_id']
        else:
            previous, previous_ref = '', ''

        if pos < len(steplist)-1:
            next = json_stepdict[pos+1]['uri_id']
            next_ref = json_stepdict[pos+1]['ref_id']
        else:
            next, next_ref = '', ''

        rendered_content = self.render_content(step.modules)

        HowToGuideStep.objects.create(
            uri_id=uri_id,
            ref_id=ref_id,
            howto=guide_howto,
            howto_title=guide_howto.title,
            title=step.title,
            steps=json_stepdict,
            first=first,
            first_ref=first_ref,
            previous=previous,
            previous_ref=previous_ref,
            next=next,
            next_ref=next_ref,
            content=rendered_content,
        )

        if step.substeps:
            for step in step.substeps:
                self.recursive_guide_step(
                    guide_howto, step, stepdict, steplist)

    def post(self, request, uri_id):
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
                HowToGuide.objects.get(howto_uri_id=uri_id,
                                       space=spaces_dict[space]).delete()
            except HowToGuide.DoesNotExist:
                pass  # The HowToGuide was not published before. Nothing to do

        # Get How To
        howto = HowTo.objects.get(uri_id=uri_id)

        # Get How To Steps
        steps = howto.steps

        # Generate stepdict
        stepdict = {}
        number = [0]
        for step in steps:
            stepdict = {**stepdict, **self.recursive_stepdict(step, 0, number)}
        steplist = list(stepdict.keys())

        json_stepdict = {}
        step_pos = 0
        for step in steplist:
            step = {
                step_pos: {
                    'uri_id': step,
                    'ref_id': stepdict[step]['ref_id'],
                    'number': stepdict[step]['number'],
                    'title': stepdict[step]['title'],
                    'current': stepdict[step]['current'],
                    'level': stepdict[step]['level'],
                }
            }
            json_stepdict = {**json_stepdict, **step}
            step_pos += 1

        # Write HowToGuide
        for space in spaces:
            guide_howto = HowToGuide.objects.create(
                howto_uri_id=howto.uri_id,
                space=spaces_dict[space],
                title=howto.title,
                first=steps[0].uri_id,
                first_ref=stepdict[steps[0].uri_id]['ref_id'],
                steps=json_stepdict,
            )

            # Write HowToGuideStep
            for step in steps:
                self.recursive_guide_step(
                    guide_howto, step, stepdict, steplist)

        # Save Successful publish to How To
        howto.is_published = True
        howto.publish_date = timezone.now()
        howto.save()

        payload = {
            'is_published': howto.is_published,
            'publish_date': howto.publish_date,
        }

        return Response(payload,
                        status=status.HTTP_200_OK)
