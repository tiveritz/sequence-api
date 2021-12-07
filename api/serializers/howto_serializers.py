from rest_framework import serializers
from django.db.models import Max
from ..models import HowTo, Step, HowToStep
from .step_serializers import StepSimpleSerializer


class HowToSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='how-to-detail',
                                               lookup_field='uri_id')

    class Meta:
        model = HowTo
        fields = ('uri_id', 'title', 'created', 'updated', 'url',)

    def create(self, validated_data):
        """
        Create a new How To
        """
        return HowTo.objects.create(**validated_data)


class HowToDetailSerializer(serializers.ModelSerializer):
    steps_url = serializers.HyperlinkedIdentityField(
        view_name='how-to-step',
        lookup_field='uri_id')
    steps = StepSimpleSerializer(many=True, read_only=True, context='context')

    class Meta:
        model = HowTo
        fields = ('uri_id', 'created', 'updated', 'is_published',
                  'publish_date', 'title', 'description', 'steps_url',
                  'steps',)
        read_only_fields = ['uri_id', 'created', 'updated', 'is_published',
                            'publish_date', ]

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class HowToStepSerializer(serializers.Serializer):
    uri_id = serializers.CharField(max_length=8)
    how_to_uri_id = serializers.CharField(max_length=8)

    def create(self, validated_data):
        """
        Link a step to a How To
        """
        step_uri_id = validated_data['uri_id']
        how_to_uri_id = validated_data['how_to_uri_id']

        how_to = HowTo.objects.get(uri_id=how_to_uri_id)
        step = Step.objects.get(uri_id=step_uri_id)

        # Set position
        how_to_steps = HowToStep.objects.filter(how_to=how_to)
        how_to_max_pos = how_to_steps.aggregate(Max('pos'))
        pos = how_to_max_pos['pos__max']
        new_pos = 0 if pos is None else pos + 1

        return HowToStep.objects.create(how_to=how_to,
                                        step=step,
                                        pos=new_pos)

    def validate(self, data):
        step_uri_id = data['uri_id']
        how_to_uri_id = data['how_to_uri_id']

        how_to = HowTo.objects.get(uri_id=how_to_uri_id)
        step = Step.objects.get(uri_id=step_uri_id)

        is_substep = HowToStep.objects.filter(how_to=how_to,
                                              step=step).exists()

        if is_substep:
            msg = 'Step already linked to How To. Duplicate not allowed'
            raise serializers.ValidationError(msg)
        return data
