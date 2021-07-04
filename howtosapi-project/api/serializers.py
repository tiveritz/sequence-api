from rest_framework import serializers
from rest_framework.response import Response
from .models import HowTo, HowToUriId, Step, StepUriId, HowToStep, Super, Explanation
from rest_framework import generics
from django.db.models import Max
from rest_framework import status


class HowToSerializer(serializers.HyperlinkedModelSerializer): 
    uri_id = serializers.SlugRelatedField(
        read_only = True,
        slug_field = 'uri_id',
        )
    url = serializers.HyperlinkedIdentityField(view_name = 'how-to-detail',
                                               lookup_field = 'uri_id')

    class Meta:
        model = HowTo
        fields = ('uri_id', 'title', 'created', 'updated', 'url')
    
    def create(self, validated_data):
        """
        Create the How To, generate a How To Uri Id and link it to the
        How To
        """
        from .functions.uri_id_generator import generate
        how_to = HowTo.objects.create(**validated_data)
        uri_id = generate(how_to.id)
        how_to_uri_id = HowToUriId(
            uri_id = uri_id,
            how_to_id = how_to
        )
        how_to_uri_id.save()

        return how_to

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
        from .functions.uri_id_generator import generate
        step = Step.objects.create(**validated_data)
        uri_id = generate(step.id)
        step_uri_id = StepUriId(
            uri_id = uri_id,
            step_id = step
        )
        step_uri_id.save()

        return step

class RecursiveField(serializers.Serializer):
	# Source: https://programmersought.com/article/62131194762/
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context = self.context)
        return serializer.data

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
    substeps = StepSimpleSerializer(many = True, read_only = True)

    class Meta:
        model = Step
        fields = ('uri_id', 'title', 'created', 'updated', 'description',
                  'substeps_url', 'substeps')
    
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

class HowToStepSerializer(serializers.Serializer):
    uri_id = serializers.CharField(max_length = 8)
    how_to_uri_id = serializers.CharField(max_length = 8)

    def create(self, validated_data):
        """
        Link a step to a How To
        """
        how_to_uri_id = validated_data['how_to_uri_id']
        step_uri_id = validated_data['uri_id']
        
        how_to = HowTo.objects.get(howtouriid__uri_id = how_to_uri_id)
        step = Step.objects.get(stepuriid__uri_id = step_uri_id)

        # Set position
        how_to_steps = HowToStep.objects.filter(how_to_id = how_to)
        how_to_max_pos = how_to_steps.aggregate(Max('pos'))
        pos = how_to_max_pos['pos__max']
        new_pos = 0 if pos == None else pos + 1

        how_to_step = HowToStep.objects.create(how_to_id = how_to,
                                               step_id = step,
                                               pos = new_pos)
        return how_to_step

    def validate(self, data):
        uri_id = data['uri_id']
        how_to_uri_id = data['how_to_uri_id']

        how_to = HowToUriId.objects.get(uri_id = how_to_uri_id)
        step = StepUriId.objects.get(uri_id = uri_id)

        is_substep = HowToStep.objects.filter(how_to_id = how_to.id,
                                              step_id = step.id).exists()

        if is_substep:
            msg = 'Step already linked to How To. Duplicate not allowed'
            raise serializers.ValidationError(msg)
        return data


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
        from .functions.circular_reference import has_circular_reference
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


class HowToDetailSerializer(serializers.ModelSerializer):
    uri_id = serializers.SlugRelatedField(read_only = True,
                                          slug_field = 'uri_id',)
    steps_url = serializers.HyperlinkedIdentityField(
        view_name = 'how-to-step',
        lookup_field = 'uri_id')
    steps = StepSimpleSerializer(many = True, read_only = True)

    class Meta:
        model = HowTo
        fields = ('uri_id', 'title', 'created', 'updated', 'description',
                  'steps_url', 'steps')
    
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

class ExplanationSerializer(serializers.HyperlinkedModelSerializer):
    uri_id = serializers.SlugRelatedField(read_only = True,
                                          slug_field = 'uri_id',)

    url = serializers.HyperlinkedIdentityField(
        view_name = 'explanation-detail',
        lookup_field = 'uri_id',)

    class Meta:
        model = Explanation
        fields = ['uri_id', 'type', 'title', 'step', 'pos', 'url']

class ExplanationDetailSerializer(serializers.ModelSerializer):
    uri_id = serializers.SlugRelatedField(read_only = True,
                                          slug_field = 'uri_id',)

    class Meta:
        model = Explanation
        fields = ['uri_id', 'type', 'title', 'step', 'pos', 'content']
