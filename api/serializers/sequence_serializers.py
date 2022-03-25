from rest_framework import serializers
from django.db.models import Max
from ..models import Sequence, Step, SequenceStep
from .step_serializers import StepSimpleSerializer


class SequenceSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='sequence-detail',
                                               lookup_field='api_id')

    class Meta:
        model = Sequence
        fields = ('api_id', 'title', 'created', 'updated', 'url',)

    def create(self, validated_data):
        """
        Create a new Sequence
        """
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
