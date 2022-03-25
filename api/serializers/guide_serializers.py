from rest_framework import serializers
from ..models import SequenceGuide, SequenceGuideStep


class SequenceGuideSerializer(serializers.ModelSerializer):
    class Meta:
        model = SequenceGuide
        fields = ('sequence_api_id', 'title', 'first', 'first_ref', 'steps')


class StepGuideSerializer(serializers.ModelSerializer):
    class Meta:
        model = SequenceGuideStep
        fields = ('api_id', 'ref_api_id', 'sequence_title', 'title', 'first',
                  'first_ref', 'previous', 'previous_ref', 'next', 'next_ref',
                  'steps', 'content',)
