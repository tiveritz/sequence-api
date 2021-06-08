from rest_framework import serializers
from .models import HowTo, HowToUriId, Step, StepUriId, HowToStep
from api.uri_id_generator import generate
from rest_framework import generics


class HowToSerializer(serializers.HyperlinkedModelSerializer): 
    uri_id = serializers.SlugRelatedField(
        read_only = True,
        slug_field = 'uri_id',
        )
    url = serializers.HyperlinkedIdentityField(
        view_name = 'how-to-detail',
        lookup_field = 'uri_id',
        )

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

class StepSerializer(serializers.HyperlinkedModelSerializer): 
    uri_id = serializers.SlugRelatedField(
        read_only = True,
        slug_field = 'uri_id',
        )
    url = serializers.HyperlinkedIdentityField(
        view_name = 'step-detail',
        lookup_field = 'uri_id',
        )

    class Meta:
        model = Step
        fields = ('uri_id', 'title', 'created', 'updated', 'url')

    def create(self, validated_data):
        """
        Create the How To, generate a How To Uri Id and link it to the
        How To
        """
        step = Step.objects.create(**validated_data)
        uri_id = generate(step.id)
        step_uri_id = StepUriId(
            uri_id = uri_id,
            step_id = step
        )
        step_uri_id.save()

        return step

class StepDetailSerializer(serializers.ModelSerializer):
    uri_id = serializers.SlugRelatedField(
        read_only = True,
        slug_field = 'uri_id',
        )

    class Meta:
        model = Step
        fields = ('uri_id', 'title', 'created', 'updated', 'description')
    
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

class HowToStepField(serializers.ModelSerializer):
    def to_representation(self, value):

        data = {
            'title' : value.step_id.title,
            'description' : value.step_id.description,
            }
        return data

class HowToDetailSerializer(serializers.HyperlinkedModelSerializer):
    uri_id = serializers.SlugRelatedField(
        read_only = True,
        slug_field = 'uri_id',
        )
    steps = StepSerializer(many = True, read_only = True)

    class Meta:
        model = HowTo
        fields = ('uri_id', 'title', 'created', 'updated', 'description', 'steps')
    
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
