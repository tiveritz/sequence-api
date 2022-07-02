from rest_framework.serializers import (ModelSerializer,
                                        HyperlinkedIdentityField,
                                        UUIDField)
from api.models import Sequence, Step
from api.base.choices import StepChoices
from api.serializers.step_serializers import StepDetailSerializer


class SequenceDetailSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(view_name='api:sequence',
                                   lookup_field='uuid',)
    step = UUIDField(read_only=True, source='step.uuid')
    linked = StepDetailSerializer(many=True,
                                  read_only=True,
                                  source='step.linked')

    class Meta:
        model = Sequence
        exclude = ['id']
        read_only_fields = ('url',
                            'uuid',
                            'created',
                            'updated',
                            'is_published',
                            'publish_date',
                            'step',
                            'linked')


class SequenceSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(view_name='api:sequence',
                                   lookup_field='uuid',)
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
                            'step')

    def create(self, validated_data):
        step = Step.objects.create(type=StepChoices.SEQUENCE)
        return Sequence.objects.create(step=step)
