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
                            'step')

    def create(self, validated_data):
        step = Step.objects.create(type=StepChoices.SEQUENCE_STEP)
        return Sequence.objects.create(step=step)
