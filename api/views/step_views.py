from django.db.models import F
from django.db.models import Max
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from core.pagination import ListPagination

from ..models import (Step, SuperStep, DecisionStep, Explanation, Module,
                      StepModule, Image)
from ..serializers.step_serializers import (StepSerializer,
                                            StepSimpleSerializer,
                                            StepDetailSerializer,
                                            SubstepSerializer,
                                            DecisionStepSerializer,
                                            StepModuleSerializer,)
from ..serializers.explanation_serializers import (ExplanationDetailSerializer,
                                                   ExplanationSimpleSerializer)
from ..serializers.media_serializers import ImageSerializer


class SubstepView(APIView):
    """
    View to Substeps
    """

    def get(self, request, uri_id):
        steps = Step.objects.get(uri_id=uri_id).substeps
        serializer = StepSimpleSerializer(steps,
                                          many=True,
                                          context={'request': request})
        return Response(serializer.data)

    def post(self, request, uri_id, format=None):
        data = request.data.copy()
        data['super_uri_id'] = uri_id
        serializer = SubstepSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_403_FORBIDDEN)

    def patch(self, request, uri_id):
        data = request.data.copy()
        method = data['method']
        super = Step.objects.get(uri_id=uri_id)

        if method == 'order':
            old_index = data['old_index']
            new_index = data['new_index']

            substep = SuperStep.objects.get(super=super, pos=old_index)

            if old_index < new_index:  # Move down
                SuperStep.objects.filter(super=super) \
                    .filter(pos__gt=old_index) \
                    .filter(pos__lte=new_index) \
                    .update(pos=F('pos') - 1)
                substep.pos = new_index
                substep.save()

            if old_index > new_index:  # Move up
                SuperStep.objects.filter(super=super) \
                    .filter(pos__lt=old_index) \
                    .filter(pos__gte=new_index) \
                    .update(pos=F('pos') + 1)
                substep.pos = new_index
                substep.save()

            return Response(status=status.HTTP_200_OK)

        if method == 'delete':
            substep_uri_id = data['uri_id']

            substep = Step.objects.get(uri_id=substep_uri_id)
            delete = SuperStep.objects.get(super=super, sub=substep)
            max_pos = SuperStep.objects.filter(
                super=super).aggregate(Max('pos'))['pos__max']
            pos = delete.pos

            delete.delete()

            if pos != max_pos:  # Move all following steps up
                SuperStep.objects.filter(super=super) \
                                 .filter(pos__gt=pos) \
                                 .filter(pos__lte=max_pos) \
                                 .update(pos=F('pos') - 1)

            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class DecisionView(APIView):
    """
    View to Decision Steps
    """

    def get(self, request, uri_id):
        decisionsteps = Step.objects.get(uri_id=uri_id).decisionsteps
        serializer = StepSimpleSerializer(decisionsteps,
                                          many=True,
                                          context={'request': request})
        return Response(serializer.data)

    def post(self, request, uri_id, format=None):
        data = request.data.copy()
        data['super_uri_id'] = uri_id
        serializer = DecisionStepSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_403_FORBIDDEN)

    def patch(self, request, uri_id):
        data = request.data.copy()
        method = data['method']
        super = Step.objects.get(uri_id=uri_id)

        if method == 'order':
            old_index = data['old_index']
            new_index = data['new_index']

            decision_step = DecisionStep.objects.get(
                super=super, pos=old_index)

            if old_index < new_index:  # Move down
                DecisionStep.objects.filter(super=super) \
                    .filter(pos__gt=old_index) \
                    .filter(pos__lte=new_index) \
                    .update(pos=F('pos') - 1)
                decision_step.pos = new_index
                decision_step.save()

            if old_index > new_index:  # Move up
                DecisionStep.objects.filter(super=super) \
                    .filter(pos__lt=old_index) \
                    .filter(pos__gte=new_index) \
                    .update(pos=F('pos') + 1)
                decision_step.pos = new_index
                decision_step.save()

            return Response(status=status.HTTP_200_OK)

        if method == 'delete':
            decision_step_uri_id = data['uri_id']

            decision_step = Step.objects.get(uri_id=decision_step_uri_id)
            delete = DecisionStep.objects.get(
                super=super, decision=decision_step)
            max_pos = DecisionStep.objects.filter(
                super=super).aggregate(Max('pos'))['pos__max']
            pos = delete.pos

            delete.delete()

            if pos != max_pos:  # Move all following steps up
                DecisionStep.objects.filter(super=super) \
                    .filter(pos__gt=pos) \
                    .filter(pos__lte=max_pos) \
                    .update(pos=F('pos') - 1)

            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class SuperDetailView(APIView):
    """
    View to Steps of a How To
    """

    def delete(self, request, uri_id, step_uri_id):
        super = Step.objects.get(uri_id=uri_id)
        sub = Step.objects.get(uri_id=step_uri_id)
        SuperStep.objects.filter(super=super,
                                 sub=sub).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class StepListView(ListAPIView):
    """
    View to Steps
    """
    queryset = Step.objects.all().order_by('-updated')
    serializer_class = StepSerializer
    pagination_class = ListPagination

    def post(self, request, format=None):
        serializer = StepSerializer(data=request.data,
                                    context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class StepDetailView(APIView):
    """
    View to Step with it's content
    """

    def get(self, request, uri_id):
        try:
            step = Step.objects.get(uri_id=uri_id)
        except Step.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = StepDetailSerializer(step,
                                          context={'request': request})
        return Response(serializer.data)

    def patch(self, request, uri_id):
        step = Step.objects.get(uri_id=uri_id)
        serializer = StepDetailSerializer(step,
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
        Step.objects.get(uri_id=uri_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class StepLinkableView(APIView):
    """
    View to Steps that can be linked to a Step
    """

    def get_substep_tree(self, step):
        substeps = SuperStep.objects.filter(super=step)

        substep_tree = []
        # Add self
        substep_tree.append(step)

        # Recursively add substeps
        for substep in substeps:
            step = Step.objects.get(uri_id=substep.sub.uri_id)
            substep_tree = self.get_substep_tree(step)
            if substep_tree:
                substep_tree.append(substep.sub)
        return substep_tree

    def get_superstep_tree(self, step):
        supersteps = SuperStep.objects.filter(sub=step)

        superstep_tree = []
        # Add self
        superstep_tree.append(step)

        # Recursively add supersteps
        for superstep in supersteps:
            step = Step.objects.get(uri_id=superstep.super.uri_id)
            superstep_tree = self.get_superstep_tree(step)
            if superstep_tree:
                superstep_tree.append(superstep.super)
        return superstep_tree

    def has_circular_reference(self, step, check):
        substeps = self.get_substep_tree(step)
        supersteps = self.get_superstep_tree(step)

        if check in substeps:
            return True
        if check in supersteps:
            return True
        return False

    def get(self, request, uri_id):
        # Can not link itself
        current_step = Step.objects.get(uri_id=uri_id)

        # Can not link a Substep of this Step
        substeps = SuperStep.objects.filter(super=current_step)
        uri_ids = [step.sub.uri_id for step in substeps]
        steps = Step.objects.exclude(uri_id=current_step.uri_id).exclude(
            uri_id__in=uri_ids).order_by('-updated')

        # Can not link a Step that is already in the parent tree
        for step in steps:
            if self.has_circular_reference(step, current_step):
                steps = steps.exclude(uri_id=step.uri_id)

        serializer = StepSimpleSerializer(steps,
                                          many=True,
                                          context={'request': request})
        return Response(serializer.data,
                        status=status.HTTP_200_OK)


class DecisionLinkableView(APIView):
    """
    View to Decision Steps that can be linked to a Step
    """

    def get(self, request, uri_id):
        # Can not link itself
        current_step = Step.objects.get(uri_id=uri_id)

        # Can not link a Substep of this Step
        decisionsteps = DecisionStep.objects.filter(super=current_step)
        uri_ids = [step.decision.uri_id for step in decisionsteps]
        steps = Step.objects.exclude(uri_id=current_step.uri_id).exclude(
            uri_id__in=uri_ids).order_by('-updated')

        serializer = StepSimpleSerializer(steps,
                                          many=True,
                                          context={'request': request})
        return Response(serializer.data,
                        status=status.HTTP_200_OK)


class StepLinkableModulesView(APIView):
    """
    View to Modules that can be linked to a Step
    """

    def get(self, request, uri_id):
        step = Step.objects.get(uri_id=uri_id)
        modules = Module.objects.filter(stepmodule__step=step)
        exclude = [
            m.explanation.uri_id for m in modules if m.explanation]
        explanations = Explanation.objects.exclude(uri_id__in=exclude)
        serializer = ExplanationDetailSerializer(explanations,
                                                 many=True,
                                                 context={'request': request})
        return Response(serializer.data,
                        status=status.HTTP_200_OK)


class StepLinkableImagesView(APIView):
    """
    View to Images that can be linked to a Step
    """

    def get(self, request, uri_id):
        step = Step.objects.get(uri_id=uri_id)
        modules = Module.objects.filter(stepmodule__step=step)
        exclude = [module.image.uri_id for module in modules if module.image]
        images = Image.objects.exclude(uri_id__in=exclude)
        serializer = ImageSerializer(images,
                                     many=True,
                                     context={'request': request})
        return Response(serializer.data,
                        status=status.HTTP_200_OK)


class StepModuleView(APIView):
    """
    View to explanations of a step
    """

    def get(self, request, uri_id):
        step = Step.objects.get(uri_id=uri_id)
        modules = step.modules
        serializer = ExplanationSimpleSerializer(modules,
                                                 many=True,
                                                 context={'request': request})
        return Response(serializer.data)

    def post(self, request, uri_id, format=None):
        data = request.data.copy()
        data['step_uri_id'] = uri_id
        serializer = StepModuleSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_403_FORBIDDEN)

    def patch(self, request, uri_id):
        data = request.data.copy()
        method = data['method']
        step = Step.objects.get(uri_id=uri_id)

        if method == 'order':
            old_index = data['old_index']
            new_index = data['new_index']

            explanation = StepModule.objects.get(step=step, pos=old_index)

            if old_index < new_index:  # Move down
                StepModule.objects.filter(step=step) \
                    .filter(pos__gt=old_index) \
                    .filter(pos__lte=new_index) \
                    .update(pos=F('pos') - 1)
                explanation.pos = new_index
                explanation.save()

            if old_index > new_index:  # Move up
                StepModule.objects.filter(step=step) \
                    .filter(pos__lt=old_index) \
                    .filter(pos__gte=new_index) \
                    .update(pos=F('pos') + 1)
                explanation.pos = new_index
                explanation.save()

            return Response(status=status.HTTP_200_OK)

        if method == 'delete':
            uri_id = data['uri_id']

            if Explanation.objects.filter(uri_id=uri_id).exists():
                explanation = Explanation.objects.get(uri_id=uri_id)
                module = Module.objects.get(explanation=explanation)
                delete = StepModule.objects.get(step=step, module=module)
            else:
                image = Image.objects.get(uri_id=uri_id)
                module = Module.objects.get(image=image)
                delete = StepModule.objects.get(step=step, module=module)
            max_pos = StepModule.objects.filter(
                step=step).aggregate(Max('pos'))['pos__max']
            pos = delete.pos

            delete.delete()

            if pos != max_pos:  # Move all following steps up
                StepModule.objects.filter(step=step) \
                    .filter(pos__gt=pos) \
                    .filter(pos__lte=max_pos) \
                    .update(pos=F('pos') - 1)

            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
