from rest_framework import serializers
from ..models import SequenceGuide, SequenceGuideStep


class SequenceGuideSerializer(serializers.ModelSerializer):
    class Meta:
        model = SequenceGuide
        fields = ('api_id', 'title', 'first')


class StepGuideSerializer(serializers.ModelSerializer):
    class Meta:
        model = SequenceGuideStep
        fields = ('api_id', 'sequence_title', 'title', 'first', 'previous', 'next', 'decision_steps', 'content',)
