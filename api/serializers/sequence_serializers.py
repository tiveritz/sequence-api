from rest_framework.serializers import ModelSerializer, HyperlinkedIdentityField, UUIDField
from api.models import Sequence, Step
from api.base.choices import StepChoices


class SequenceSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(view_name='api:sequence', lookup_field='uuid',)
    step = UUIDField(read_only=True, source='step.uuid')

    class Meta:
        model = Sequence
        exclude = ['id']
        read_only_fields = ('url',
                            'uuid',
                            'created',
                            'updated',
                            'is_published',
                            'publish_date',
                            'step',)

    def create(self, validated_data):
        step = Step.objects.create(type=StepChoices.SEQUENCE_STEP)
        return Sequence.objects.create(step=step)


'''

from rest_framework import serializers
from django.db.models import Max
from ..models import Sequence, Step, SequenceStep
from .step_serializers import StepSimpleSerializer


class SequenceSerializer(ModelSerializer):
    view_name = 'sequence-detail'
    lookup_field = 'api_id'

    url = HyperlinkedIdentityField(view_name=view_name, lookup_field=lookup_field)

    class Meta:
        model = Sequence
        fields = '__all__'

    def create(self, validated_data):
        return Sequence.objects.create(**validated_data)


class SequenceDetailSerializer(serializers.ModelSerializer):
    steps_url = serializers.HyperlinkedIdentityField(
        view_name='sequence-step',
        lookup_field='api_id')
    steps = StepSimpleSerializer(many=True, read_only=True, context='context')

    class Meta:
        model = Sequence
        fields = ('api_id', 'created', 'updated', 'is_published',
                  'publish_date', 'title', 'description', 'steps_url',
                  'steps',)
        read_only_fields = ['api_id', 'created', 'updated', 'is_published',
                            'publish_date', ]

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class SequenceStepSerializer(serializers.Serializer):
    api_id = serializers.UUIDField()
    sequence_api_id = serializers.UUIDField()

    def create(self, validated_data):
        """
        Link a step to a Sequence
        """
        step_api_id = validated_data['api_id']
        sequence_api_id = validated_data['sequence_api_id']

        sequence = Sequence.objects.get(api_id=sequence_api_id)
        step = Step.objects.get(api_id=step_api_id)

        # Set position
        sequence_steps = SequenceStep.objects.filter(sequence=sequence)
        sequence_max_pos = sequence_steps.aggregate(Max('pos'))
        pos = sequence_max_pos['pos__max']
        new_pos = 0 if pos is None else pos + 1

        return SequenceStep.objects.create(sequence=sequence,
                                        step=step,
                                        pos=new_pos)

    def validate(self, data):
        step_api_id = data['api_id']
        sequence_api_id = data['sequence_api_id']

        sequence = Sequence.objects.get(api_id=sequence_api_id)
        step = Step.objects.get(api_id=step_api_id)

        is_substep = SequenceStep.objects.filter(sequence=sequence,
                                              step=step).exists()

        if is_substep:
            msg = 'Step already linked to Sequence. Duplicate not allowed'
            raise serializers.ValidationError(msg)
        return data
'''
