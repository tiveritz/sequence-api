from rest_framework import serializers
from ..models import GuideHowTo, GuideStep


class HowToGuideSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuideHowTo
        fields = ('howto_uri_id', 'title', 'first', 'first_ref', 'steps')

class StepGuideSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuideStep
        fields = ('uri_id', 'ref_id', 'howto_title', 'title', 'first',
                  'first_ref', 'previous', 'previous_ref', 'next', 'next_ref',
                  'steps', 'content',
                 )