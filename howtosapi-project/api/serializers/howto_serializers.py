from rest_framework import serializers
from django.db.models import Max
from ..models import HowTo, HowToUriId, Step, StepUriId, HowToStep
from ..functions.uri_id_generator import generate
from .step_serializers import StepSimpleSerializer


class HowToSerializer(serializers.HyperlinkedModelSerializer): 
    uri_id = serializers.SlugRelatedField(
        read_only = True,
        slug_field = 'uri_id',
        )
    url = serializers.HyperlinkedIdentityField(view_name = 'how-to-detail',
                                               lookup_field = 'uri_id')

    class Meta:
        model = HowTo
        fields = ('uri_id', 'title', 'created', 'updated', 'url')
    
    def create(self, validated_data):
        """
        Create the How To, generate a How To Uri Id and link it to the
        How To
        """
        how_to = HowTo.objects.create(**validated_data)
        uri_id = generate(how_to.id)
        how_to_uri_id = HowToUriId(
            uri_id = uri_id,
            how_to_id = how_to
        )
        how_to_uri_id.save()

        return how_to


class HowToDetailSerializer(serializers.ModelSerializer):
    uri_id = serializers.SlugRelatedField(read_only = True,
                                          slug_field = 'uri_id',)
    steps_url = serializers.HyperlinkedIdentityField(
        view_name = 'how-to-step',
        lookup_field = 'uri_id')
    steps = StepSimpleSerializer(many = True, read_only = True, context = 'context')

    class Meta:
        model = HowTo
        fields = ('uri_id', 'title', 'created', 'updated', 'description',
                  'steps_url', 'steps')
    
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class HowToStepSerializer(serializers.Serializer):
    uri_id = serializers.CharField(max_length = 8)
    how_to_uri_id = serializers.CharField(max_length = 8)

    def create(self, validated_data):
        """
        Link a step to a How To
        """
        how_to_uri_id = validated_data['how_to_uri_id']
        step_uri_id = validated_data['uri_id']
        
        how_to = HowTo.objects.get(howtouriid__uri_id = how_to_uri_id)
        step = Step.objects.get(stepuriid__uri_id = step_uri_id)

        # Set position
        how_to_steps = HowToStep.objects.filter(how_to_id = how_to)
        how_to_max_pos = how_to_steps.aggregate(Max('pos'))
        pos = how_to_max_pos['pos__max']
        new_pos = 0 if pos == None else pos + 1

        how_to_step = HowToStep.objects.create(how_to_id = how_to,
                                               step_id = step,
                                               pos = new_pos)
        return how_to_step

    def validate(self, data):
        uri_id = data['uri_id']
        how_to_uri_id = data['how_to_uri_id']

        how_to = HowToUriId.objects.get(uri_id = how_to_uri_id)
        step = StepUriId.objects.get(uri_id = uri_id)

        is_substep = HowToStep.objects.filter(how_to_id = how_to.id,
                                              step_id = step.id).exists()

        if is_substep:
            msg = 'Step already linked to How To. Duplicate not allowed'
            raise serializers.ValidationError(msg)
        return data
