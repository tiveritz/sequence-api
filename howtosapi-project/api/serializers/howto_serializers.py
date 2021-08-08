from rest_framework import serializers
from django.db.models import Max
from ..models import HowTo, Step, HowToStep
from ..functions.uri_id import generate_uri_id
from .step_serializers import StepSimpleSerializer


class HowToSerializer(serializers.HyperlinkedModelSerializer): #TEST OK
    url = serializers.HyperlinkedIdentityField(view_name = 'how-to-detail',
                                               lookup_field = 'uri_id')

    class Meta:
        model = HowTo
        fields = ('uri_id', 'title', 'created', 'updated', 'url')
    
    def create(self, validated_data): #TEST OK
        """
        Create a new How To
        """
        return HowTo.objects.create(**validated_data)


class HowToDetailSerializer(serializers.ModelSerializer): #TEST OK
    steps_url = serializers.HyperlinkedIdentityField(
        view_name = 'how-to-step',
        lookup_field = 'uri_id')
    steps = StepSimpleSerializer(many = True, read_only = True, context = 'context')

    class Meta:
        model = HowTo
        fields = ('uri_id', 'title', 'created', 'updated', 'description', 'steps_url', 'steps')
        read_only_fields = ['uri_id', 'created', 'updated']
    
    def partial_update(self, request, *args, **kwargs): #TEST OK
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class HowToStepSerializer(serializers.Serializer):
    uri_id = serializers.CharField(max_length = 8)
    how_to_uri_id = serializers.CharField(max_length = 8)

    def create(self, validated_data): #TEST OK
        """
        Link a step to a How To
        """
        step_uri_id = validated_data['uri_id']
        how_to_uri_id = validated_data['how_to_uri_id']
        
        how_to = HowTo.objects.get(uri_id = how_to_uri_id)
        step = Step.objects.get(uri_id = step_uri_id)

        # Set position
        how_to_steps = HowToStep.objects.filter(how_to = how_to)
        how_to_max_pos = how_to_steps.aggregate(Max('pos'))
        pos = how_to_max_pos['pos__max']
        new_pos = 0 if pos == None else pos + 1

        how_to_step = HowToStep.objects.create(how_to = how_to,
                                               step = step,
                                               pos = new_pos)
        return how_to_step

    def validate(self, data): #TEST OK
        step_uri_id = data['uri_id']
        how_to_uri_id = data['how_to_uri_id']

        how_to = HowTo.objects.get(uri_id = how_to_uri_id)
        step = Step.objects.get(uri_id = step_uri_id)

        is_substep = HowToStep.objects.filter(how_to = how_to,
                                              step = step).exists()

        if is_substep:
            msg = 'Step already linked to How To. Duplicate not allowed'
            raise serializers.ValidationError(msg)
        return data
