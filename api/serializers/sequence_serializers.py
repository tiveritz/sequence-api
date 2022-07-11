from rest_framework.serializers import (CharField,
                                        ModelSerializer,
                                        HyperlinkedIdentityField,
                                        UUIDField)
from api.models import Sequence, Step
from api.base.choices import StepChoices
from api.serializers.step_serializers import StepSerializer


class SequenceBaseSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(view_name='api:sequence',
                                   lookup_field='uuid')
    uuid = UUIDField(read_only=True, source='step.uuid')
    title = CharField(source='step.title')


class SequenceSerializer(SequenceBaseSerializer):
    linked = StepSerializer(many=True,
                            read_only=True,
                            source='step.linked')

    class Meta:
        model = Sequence
        exclude = ['id', 'step']

    def update(self, instance, validated_data):
        instance.step.title = validated_data['step']['title']
        instance.step.save()

        return instance


class SequencesSerializer(SequenceBaseSerializer):
    class Meta:
        model = Sequence
        exclude = ['id', 'step']

    def create(self, validated_data):
        step = Step.objects.create(type=StepChoices.SEQUENCE,
                                   title=validated_data['step']['title'])
        return Sequence.objects.create(step=step)
