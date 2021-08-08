from django.db.models import F
from django.db.models import Max
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import Step, SuperStep, Explanation, StepModule, Image
from ..serializers.step_serializers import (StepSerializer,
                                            StepSimpleSerializer,
                                            StepDetailSerializer,
                                            SubstepSerializer,
                                            StepExplanationSerializer,)
from ..serializers.explanation_serializers import (ExplanationDetailSerializer,
                                                   ExplanationSimpleSerializer)
from ..serializers.media_serializers import ImageSerializer


class SubstepView(APIView):
    """
    View to Substeps
    """
    def get(self, request, uri_id): #TEST OK
        steps = Step.objects.get(uri_id = uri_id).substeps
        serializer = StepSimpleSerializer(steps,
                                          many = True,
                                          context = {'request' : request})
        return Response(serializer.data)

    def post(self, request, uri_id, format = None): #TEST OK
        data = request.data
        data['super_uri_id'] = uri_id
        serializer = SubstepSerializer(data = data)

        if serializer.is_valid():
            serializer.save()
            return Response(status = status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status = status.HTTP_403_FORBIDDEN)

    def patch(self, request, uri_id): #TEST OK
        data = request.data
        method = data['method']
        super = Step.objects.get(uri_id=uri_id)

        if method == 'order':
            old_index = data['old_index']
            new_index = data['new_index']

            substep = SuperStep.objects.get(super=super, pos=old_index)

            if old_index < new_index: # Move down
                SuperStep.objects.filter(super = super) \
                             .filter(pos__gt = old_index) \
                             .filter(pos__lte = new_index) \
                             .update(pos = F('pos') - 1)
                substep.pos = new_index
                substep.save()

            if old_index > new_index: # Move up
                SuperStep.objects.filter(super = super) \
                             .filter(pos__lt = old_index) \
                             .filter(pos__gte = new_index) \
                             .update(pos = F('pos') + 1)
                substep.pos = new_index
                substep.save()

            return Response(status = status.HTTP_200_OK)

        if method == 'delete':
            substep_uri_id = data['uri_id']
            
            substep = Step.objects.get(stepuriid__uri_id = substep_uri_id)
            delete = Super.objects.get(super_id = step, step_id = substep)
            max_pos = Super.objects.filter(super_id = step).aggregate(Max('pos'))['pos__max']
            pos = delete.pos

            delete.delete()

            if pos != max_pos: # Move all following steps up
                Super.objects.filter(super_id = step.id) \
                                 .filter(pos__gt = pos) \
                                 .filter(pos__lte = max_pos) \
                                 .update(pos = F('pos') - 1)

            return Response(status = status.HTTP_200_OK)
        return Response(status = status.HTTP_400_BAD_REQUEST)


class SuperDetailView(APIView): #TEST OK
    """
    View to Steps of a How To
    """
    def delete(self, request, uri_id, step_uri_id): #TEST OK
        super = Step.objects.get(uri_id = uri_id)
        sub = Step.objects.get(uri_id = step_uri_id)
        SuperStep.objects.filter(super = super,
                                 sub = sub).delete()
        return Response(status = status.HTTP_204_NO_CONTENT)


class StepListView(APIView): #TEST OK
    """
    View to Steps
    """
    def get(self, request): #TEST OK
        steps = Step.objects.all().order_by('-updated')
        serializer = StepSerializer(
            steps,
            many = True,
            context = {'request' : request}
            )
        return Response(serializer.data)

    def post(self, request, format = None): #TEST OK
        serializer = StepSerializer(data = request.data,
                                    context = {'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status = status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status = status.HTTP_400_BAD_REQUEST)


class StepDetailView(APIView): #TEST OK
    """
    View to Step with it's content
    """
    def get(self, request, uri_id): #TEST OK
        try:
            step = Step.objects.get(uri_id = uri_id)
        except Step.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = StepDetailSerializer(step,
                                          context = {'request': request})
        return Response(serializer.data)
    
    def patch(self, request, uri_id): #TEST OK
        step = Step.objects.get(uri_id = uri_id)
        serializer = StepDetailSerializer(step,
                                          data = request.data,
                                          partial = True,
                                          context = {'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status = status.HTTP_200_OK)
        return Response(serializer.errors,
                        status = status.HTTP_400_BAD_REQUEST)

    def delete(self, request, uri_id): #TEST OK
        Step.objects.get(uri_id = uri_id).delete()
        return Response(status = status.HTTP_204_NO_CONTENT)


class StepLinkableView(APIView):
    """
    View to Steps that can be linked to a Step
    """
    def get_substep_tree(self, step):
        substeps = Super.objects.filter(super_id = step.id)

        substep_tree = []
        # Add own id
        substep_tree.append(step)

        # Recursively add substeps
        for substep in substeps:
            step = Step.objects.get(id = substep.step_id.id)
            substep_tree = self.get_substep_tree(step)
            if substep_tree:
                substep_tree.append(substep.step_id)
        return substep_tree
    
    def get_superstep_tree(self, step):
        supersteps = Super.objects.filter(step_id = step.id)

        superstep_tree = []
        # Add own id
        superstep_tree.append(step)

        # Recursively add supersteps
        for superstep in supersteps:
            step = Step.objects.get(id = superstep.super_id.id)
            superstep_tree = self.get_superstep_tree(step)
            if superstep_tree:
                superstep_tree.append(superstep.step_id)
        return superstep_tree

    def has_circular_reference(self, step, check):
        substeps = self.get_substep_tree(step)
        #substeps.remove(step)
        supersteps = self.get_superstep_tree(step)
        #upersteps.remove(step)

        if check in substeps:
            return True
        if check in supersteps:
            return True
        return False
        

    def get(self, request, uri_id):
        # Can not link itself
        current_step = Step.objects.get(stepuriid__uri_id = uri_id)

        # Can not link a Substep of this Step
        substeps = Super.objects.filter(super_id = current_step.id).values_list('step_id')
                
        steps = Step.objects.exclude(id = current_step.id).exclude(id__in = substeps).order_by('-updated')

        # Can not link a Step that is already in the parent tree
        for step in steps:
            if self.has_circular_reference(step, current_step):
                steps = steps.exclude(id = step.id)

        serializer = StepSimpleSerializer(steps,
                                          many = True,
                                          context = {'request' : request})
        return Response(serializer.data,
                        status = status.HTTP_200_OK)


class StepLinkableModulesView(APIView):
    """
    View to Modules that can be linked to a Step
    """
    def get(self, request, uri_id):
        step = Step.objects.get(stepuriid__uri_id = uri_id)
        step_explanations = StepExplanation.objects.filter(step = step)
        exclude = [module.explanation_id for module in step_explanations if not module.image]
        explanations = Explanation.objects.exclude(id__in = exclude)
        serializer = ExplanationDetailSerializer(explanations,
                                                 many = True,
                                                 context = {'request' : request})
        return Response(serializer.data,
                status = status.HTTP_200_OK)

class StepLinkableImagesView(APIView):
    """
    View to Images that can be linked to a Step
    """
    def get(self, request, uri_id):
        step = Step.objects.get(stepuriid__uri_id = uri_id)
        images = Image.objects.exclude(id__in = step.images)
        serializer = ImageSerializer(images,
                                     many = True,
                                     context = {'request' : request})
        return Response(serializer.data,
                status = status.HTTP_200_OK)

class StepExplanationView(APIView):
    """
    View to explanations of a step
    """
    def get(self, request, uri_id):
        step = Step.objects.get(stepuriid__uri_id = uri_id)
        explanations = step.explanations
        serializer = ExplanationSimpleSerializer(explanations,
                                          many = True,
                                          context = {'request' : request})
        return Response(serializer.data)

    def post(self, request, uri_id, format = None):
        data = request.data
        data['step_uri_id'] = uri_id
        serializer = StepExplanationSerializer(data = data)

        if serializer.is_valid():
            serializer.save()
            return Response(status = status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status = status.HTTP_403_FORBIDDEN)

    def patch(self, request, uri_id):
        data = request.data
        method = data['method']
        step = Step.objects.get(stepuriid__uri_id = uri_id)

        if method == 'order':
            old_index = data['old_index']
            new_index = data['new_index']

            explanation = StepExplanation.objects.get(step = step, pos = old_index)

            if old_index < new_index: # Move down
                StepExplanation.objects.filter(step = step) \
                                       .filter(pos__gt = old_index) \
                                       .filter(pos__lte = new_index) \
                                       .update(pos = F('pos') - 1)
                explanation.pos = new_index
                explanation.save()

            if old_index > new_index: # Move up
                StepExplanation.objects.filter(step = step) \
                                       .filter(pos__lt = old_index) \
                                       .filter(pos__gte = new_index) \
                                       .update(pos = F('pos') + 1)
                explanation.pos = new_index
                explanation.save()

            return Response(status = status.HTTP_200_OK)

        if method == 'delete':
            uri_id = data['uri_id']
            
            if Explanation.objects.filter(explanationuriid__uri_id = uri_id).exists():
                explanation = Explanation.objects.get(explanationuriid__uri_id = uri_id)
                delete = StepExplanation.objects.get(step = step, explanation = explanation)
            else:
                image = Image.objects.get(uri_id = uri_id)
                delete = StepExplanation.objects.get(step = step, image = image)
            max_pos = StepExplanation.objects.filter(step = step).aggregate(Max('pos'))['pos__max']
            pos = delete.pos

            delete.delete()

            if pos != max_pos: # Move all following steps up
                StepExplanation.objects.filter(step = step) \
                                 .filter(pos__gt = pos) \
                                 .filter(pos__lte = max_pos) \
                                 .update(pos = F('pos') - 1)

            return Response(status = status.HTTP_200_OK)
        return Response(status = status.HTTP_400_BAD_REQUEST)
