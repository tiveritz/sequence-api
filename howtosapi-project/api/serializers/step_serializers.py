from rest_framework import serializers
from django.db.models import Max
from ..models import Step, StepUriId, Super, Explanation, StepExplanation
from ..functions.uri_id_generator import generate
from ..functions.circular_reference import has_circular_reference
from .recursive_serializers import RecursiveField
from .explanation_serializers import ExplanationSimpleSerializer


class StepSerializer(serializers.HyperlinkedModelSerializer): 
    uri_id = serializers.SlugRelatedField(read_only = True,
                                          slug_field = 'uri_id',)
    url = serializers.HyperlinkedIdentityField(view_name = 'step-detail',
                                               lookup_field = 'uri_id',)

    class Meta:
        model = Step
        fields = ('uri_id', 'title', 'created', 'updated', 'is_super', 'url')

    def create(self, validated_data):
        """
        Create the How To, generate a How To Uri Id and link it to the
        How To
        """
        step = Step.objects.create(**validated_data)
        uri_id = generate(step.id)
        step_uri_id = StepUriId(
            uri_id = uri_id,
            step_id = step
        )
        step_uri_id.save()

        return step


class StepSimpleSerializer(serializers.HyperlinkedModelSerializer): 
    uri_id = serializers.SlugRelatedField(read_only = True,
                                          slug_field = 'uri_id',)
    url = serializers.HyperlinkedIdentityField(
        view_name = 'step-detail',
        lookup_field = 'uri_id',)
    
    substeps = RecursiveField(many = True)

    class Meta:
        model = Step
        fields = ('uri_id', 'title', 'is_super', 'url', 'substeps')


class StepDetailSerializer(serializers.ModelSerializer):
    uri_id = serializers.SlugRelatedField(read_only = True,
                                          slug_field = 'uri_id',)
    substeps_url = serializers.HyperlinkedIdentityField(
        view_name = 'sub-step',
        lookup_field = 'uri_id',)
    explanations_url = serializers.HyperlinkedIdentityField(
        view_name = 'step-explanation',
        lookup_field = 'uri_id',)
    substeps = StepSimpleSerializer(many = True, read_only = True, context = 'context')
    explanations = ExplanationSimpleSerializer(many = True, read_only = True, context = 'context')

    class Meta:
        model = Step
        fields = ('uri_id', 'title', 'created', 'updated', 'description',
                  'substeps_url', 'substeps', 'explanations_url', 'explanations')
    
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class SubstepSerializer(serializers.Serializer):
    uri_id = serializers.CharField(max_length = 8)
    super_uri_id = serializers.CharField(max_length = 8)

    def create(self, validated_data):
        """
        Link a step to a How To
        """
        super_uri_id = validated_data['super_uri_id']
        step_uri_id = validated_data['uri_id']

        super = Step.objects.get(stepuriid__uri_id = super_uri_id)
        step = Step.objects.get(stepuriid__uri_id = step_uri_id)

        # Set position
        super_steps = Super.objects.filter(super_id = super)
        super_max_pos = super_steps.aggregate(Max('pos'))
        pos = super_max_pos['pos__max']
        new_pos = 0 if pos == None else pos + 1

        super_step = Super.objects.create(super_id = super,
                                          step_id = step,
                                          pos = new_pos)
        return super_step


    def validate(self, data):
        super_uri_id = data['super_uri_id']
        step_uri_id = data['uri_id']

        # Check for duplicate
        super = Step.objects.get(stepuriid__uri_id = super_uri_id)
        step = Step.objects.get(stepuriid__uri_id = step_uri_id)

        is_substep = Super.objects.filter(super_id = super.id,
                                          step_id = step.id).exists()

        if is_substep:
            msg = 'Step already linked to Superstep. Duplicate not allowed'
            raise serializers.ValidationError(msg)
        
        # Check for circular reference
        if has_circular_reference(step, super):
            msg = 'Step already linked to Superstep tree. Circular reference not allowed'
            raise serializers.ValidationError(msg)

        return data
    
    def destroy(self, validated_data):
        how_to_uri_id = validated_data['how_to_uri_id']
        step_uri_id = validated_data['uri_id']

        return self


class StepExplanationSerializer(serializers.Serializer):
    uri_id = serializers.CharField(max_length = 8)
    step_uri_id = serializers.CharField(max_length = 8)

    def create(self, validated_data):
        """
        Link a step to a How To
        """
        step_uri_id = validated_data['step_uri_id']
        explanation_uri_id = validated_data['uri_id']

        step = Step.objects.get(stepuriid__uri_id = step_uri_id)
        explanation = Explanation.objects.get(explanationuriid__uri_id = explanation_uri_id)

        # Set position
        explanations = StepExplanation.objects.filter(step = step)
        explanation_max_pos = explanations.aggregate(Max('pos'))
        pos = explanation_max_pos['pos__max']
        new_pos = 0 if pos == None else pos + 1

        step_explanation = StepExplanation.objects.create(step = step,
                                                          explanation = explanation,
                                                          pos = new_pos)
        return step_explanation

    def validate(self, data):
        step_uri_id = data['step_uri_id']
        explanation_uri_id = data['uri_id']

        # Check for duplicate
        step = Step.objects.get(stepuriid__uri_id = step_uri_id)
        explanation = Explanation.objects.get(explanationuriid__uri_id = explanation_uri_id)

        has_explanation = StepExplanation.objects.filter(step = step,
                                                         explanation = explanation).exists()

        if has_explanation:
            msg = 'Explanation already linked to Step. Duplicate not allowed'
            raise serializers.ValidationError(msg)

        return data
    
    '''
    def destroy(self, validated_data):
        how_to_uri_id = validated_data['how_to_uri_id']
        explanation_uri_id = validated_data['uri_id']

        return self
    '''