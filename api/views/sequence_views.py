import copy
from re import A
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


class SequenceNode():
    def __init__(self, step, guide_sequence, main_sequence=None, parent=None):
        self.step = step
        self.parent = parent
        self.guide_sequence = guide_sequence
        self.main_sequence = main_sequence
        self.substep_nodes = []
        self.decision_nodes = []
        
        for step in step.substeps:
            sequence_node = SequenceNode(step, guide_sequence, parent=self)
            self.substep_nodes.append(sequence_node)
        
        for step in step.decisionsteps:
            sequence_node = SequenceNode(step, guide_sequence, parent=self)
            self.decision_nodes.append(sequence_node)

    def _get_first(self):
        return self.guide_sequence.first

    def _get_previous(self):
        if self.main_sequence:
            index = self.main_sequence.index(self.step)
            if index != 0:
                return self.main_sequence[index - 1].api_id

        if self.parent and self.parent.substep_nodes:
            index = self.parent.substep_nodes.index(self)
            if index != 0:
                return self.parent.substep_nodes[index - 1].step.api_id
            return self.parent.step.api_id
        
        if self.parent and self.parent.decision_nodes:
            return self.parent.step.api_id

        return None
        
        
            #if self.parent and self.parent.substep_nodes:
            #    index = self.parent.substep_nodes.index(self.step)
            #    if index != 0:
            #        return self.parent.substep_nodes[index - 1].step.api_id

            #if self.parent and self.parent.decision_nodes:
            #    return self.parent.step.api_id

    def _get_next(self):
        if self.decision_nodes:
            return
        if self.substep_nodes:
            return self.substep_nodes[0].step.api_id
        elif self.parent:
            return self._recursive_next_step_parent(self)

        else:
            try:
                index = self.main_sequence.index(self.step)
                if index < len(self.main_sequence) - 1:
                    return self.main_sequence[index + 1].api_id
            except ValueError:
                return
    
    def _recursive_next_step_parent(self, node):
        if node.parent is None:
            try:
                index = node.main_sequence.index(node.step)
                if index < len(node.main_sequence) - 1:
                    return node.main_sequence[index + 1].api_id
            except ValueError:
                return None
        
        if node.parent.parent is not None and node.parent.parent.decision_nodes:
            if node.parent.substep_nodes:
                index = node.parent.substep_nodes.index(node)
                if index < len(node.parent.substep_nodes) - 1:
                    return node.parent.substep_nodes[index + 1].step.api_id
            
            if node.parent.parent.parent is not None:
                return self._recursive_next_step_parent(node.parent.parent.parent)
            else:
                index = node.parent.parent.main_sequence.index(node.parent.parent.step)
                if index < len(node.parent.parent.main_sequence) - 1:
                    return node.parent.parent.main_sequence[index + 1].api_id
                
        try:
            index = node.parent.substep_nodes.index(node)
            if index < len(node.parent.substep_nodes) - 1:
                return node.parent.substep_nodes[index + 1].step.api_id
            
        except ValueError:
            index = node.parent.decision_nodes.index(node)
            if index < len(node.parent.decision_nodes) - 1:
                return node.parent.decision_nodes[index + 1].step.api_id
        
        return self._recursive_next_step_parent(node.parent)
    
    
    def render(self):
        decision_steps = [str(node.step.api_id) for node in self.decision_nodes]
        SequenceGuideStep.objects.create(
            api_id=self.step.api_id,
            sequence=self.guide_sequence,
            sequence_title=self.guide_sequence.title,
            title=self.step.title,
            decision_steps=','.join(decision_steps),
            first=self._get_first(),
            previous=self._get_previous(),
            next=self._get_next(),
            content=self._get_content(),
        )

        for node in self.substep_nodes:
            node.render()
        
        for node in self.decision_nodes:
            node.render()
        

    def _get_content(self):
        if self.step.modules:
            rendered = ''
            for module in self.step.modules:
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
                SequenceGuide.objects.get(api_id=api_id,
                                       space=spaces_dict[space]).delete()
            except SequenceGuide.DoesNotExist:
                pass  # The SequenceGuide was not published before. Nothing to do

        # Get Sequence
        sequence = Sequence.objects.get(api_id=api_id)
        
        # Get Sequence Steps
        steps = sequence.steps

        # Write SequenceGuide
        for space in spaces:
            guide_sequence = SequenceGuide.objects.create(
                api_id=sequence.api_id,
                space=spaces_dict[space],
                title=sequence.title,
                first=steps[0].api_id,
            )

            for step in steps:
                sequence_node = SequenceNode(step, guide_sequence, steps)
                sequence_node.render()


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
