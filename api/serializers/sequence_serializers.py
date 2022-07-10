from rest_framework.serializers import (CharField,
                                        ModelSerializer,
                                        HyperlinkedIdentityField,
                                        UUIDField)
from api.models import Sequence, Step
from api.base.choices import StepChoices
from api.serializers.step_serializers import StepDetailSerializer


class SequenceDetailSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(view_name='api:sequence',
                                   lookup_field='uuid',)
    step = UUIDField(read_only=True, source='step.uuid')
    title = CharField(read_only=True, source='step.title')
    linked = StepDetailSerializer(many=True,
                                  read_only=True,
                                  source='step.linked')

    class Meta:
        model = Sequence
        exclude = ['id']


class SequenceSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(view_name='api:sequence',
                                   lookup_field='uuid',)
    step = UUIDField(read_only=True, source='step.uuid')
    title = CharField(required=True, source='step.title')

    class Meta:
        model = Sequence
        exclude = ['id']

    def create(self, validated_data):
        step = Step.objects.create(type=StepChoices.SEQUENCE,
                                   title=validated_data['step']['title'])
        return Sequence.objects.create(step=step)
