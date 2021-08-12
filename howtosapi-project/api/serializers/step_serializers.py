from rest_framework import serializers
from django.db.models import Max
from ..models import Step, SuperStep, Explanation, StepModule, Image
from ..functions.uri_id import generate_uri_id
from ..functions.circular_reference import has_circular_reference
from .recursive_serializers import RecursiveField
from .module_serializer import ModuleListSerializer


class StepSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='step-detail',
                                               lookup_field='uri_id',)

    class Meta:
        model = Step
        fields = ('uri_id', 'title', 'created', 'updated', 'is_super', 'url')

    def create(self, validated_data):
        """
        Create a new Step
        """
        return Step.objects.create(**validated_data)


class StepSimpleSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='step-detail',
        lookup_field='uri_id',)
    
    substeps = RecursiveField(many=True)

    class Meta:
        model = Step
        fields = ('uri_id', 'title', 'is_super', 'url', 'substeps')


class StepDetailSerializer(serializers.ModelSerializer): 
    substeps_url = serializers.HyperlinkedIdentityField(
        view_name='sub-step',
        lookup_field='uri_id',)
    modules_url = serializers.HyperlinkedIdentityField(
        view_name='step-explanation',
        lookup_field='uri_id',)
    substeps = StepSimpleSerializer(many=True, read_only=True, context='context')
    modules = ModuleListSerializer(many=True, read_only=True, context='context')

    class Meta:
        model = Step
        fields = ('uri_id', 'title', 'created', 'updated', 'description',
                  'substeps_url', 'substeps', 'modules_url', 'modules')
        read_only_fields = ['uri_id', 'created', 'updated']
    
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class SubstepSerializer(serializers.Serializer):
    uri_id = serializers.CharField(max_length=8)
    super_uri_id = serializers.CharField(max_length=8)

    def create(self, validated_data):
        """
        Link a step to a How To
        """
        super_uri_id = validated_data['super_uri_id']
        sub_uri_id = validated_data['uri_id']

        super = Step.objects.get(uri_id=super_uri_id)
        sub = Step.objects.get(uri_id=sub_uri_id)

        # Set position
        super_steps = SuperStep.objects.filter(super=super)
        super_max_pos = super_steps.aggregate(Max('pos'))
        pos = super_max_pos['pos__max']
        new_pos = 0 if pos == None else pos + 1

        super_step = SuperStep.objects.create(super=super,
                                              sub=sub,
                                              pos=new_pos)
        return super_step

    def validate(self, data):
        super_uri_id = data['super_uri_id']
        step_uri_id = data['uri_id']

        # Check for duplicate
        super = Step.objects.get(uri_id=super_uri_id)
        sub = Step.objects.get(uri_id=step_uri_id)

        is_substep = SuperStep.objects.filter(super=super,
                                              sub=sub).exists()

        if is_substep:
            msg = 'Step already linked to Superstep. Duplicate not allowed'
            raise serializers.ValidationError(msg)
        
        # Check for circular reference
        if has_circular_reference(sub, super):
            msg = 'Step already linked to Superstep tree. Circular reference not allowed'
            raise serializers.ValidationError(msg)

        return data


class StepExplanationSerializer(serializers.Serializer):
    uri_id = serializers.CharField(max_length=8)
    step_uri_id = serializers.CharField(max_length=8)
    type = serializers.CharField(max_length=128)

    def create(self, validated_data):
        """
        Link a step to a How To
        """
        step_uri_id = validated_data['step_uri_id']
        uri_id = validated_data['uri_id']

        step = Step.objects.get(uri_id = step_uri_id)

        # Set position
        explanations = StepModule.objects.filter(step=step)
        explanation_max_pos = explanations.aggregate(Max('pos'))
        pos = explanation_max_pos['pos__max']
        new_pos = 0 if pos == None else pos + 1

        # Set linked content
        if validated_data['type'] == 'explanation':
            explanation = Explanation.objects.get(uri_id=uri_id)
            step_explanation = StepModule.objects.create(step=step,
                                                         explanation=explanation,
                                                         pos=new_pos)
        elif validated_data['type'] == 'image':
            image = Image.objects.get(uri_id=uri_id)
            step_explanation = StepModule.objects.create(step=step,
                                                         image=image,
                                                         pos=new_pos)
        
        return step_explanation

    def validate(self, data):
        step_uri_id = data['step_uri_id']
        uri_id = data['uri_id']
        type = data['type']

        # Check for duplicate
        step = Step.objects.get(uri_id=step_uri_id)

        if type == 'explanation':
            explanation = Explanation.objects.get(uri_id=uri_id)
            has_duplicate = StepModule.objects.filter(step=step,
                                                      explanation=explanation).exists()
        elif type == 'image':
            image = Image.objects.get(uri_id=uri_id)
            has_duplicate = StepModule.objects.filter(step=step,
                                                      image=image).exists()

        if has_duplicate:
            msg = 'Explanation already linked to Step. Duplicate not allowed'
            raise serializers.ValidationError(msg)

        return data
