from rest_framework import serializers
from django.db.models import Max
from ..models import Explanation, ExplanationUriId
from ..functions.uri_id_generator import generate


class ExplanationSerializer(serializers.HyperlinkedModelSerializer):
    uri_id = serializers.SlugRelatedField(read_only = True,
                                          slug_field = 'uri_id',)

    url = serializers.HyperlinkedIdentityField(
        view_name = 'explanation-detail',
        lookup_field = 'uri_id',)

    class Meta:
        model = Explanation
        fields = ['uri_id', 'type', 'title', 'created', 'updated', 'url']

    def create(self, validated_data):
        """
        Create the How To, generate a How To Uri Id and link it to the
        How To
        """
        explanation = Explanation.objects.create(**validated_data)
        uri_id = generate(explanation.id)
        explanation_uri_id = ExplanationUriId(
            uri_id = uri_id,
            explanation = explanation
        )
        explanation_uri_id.save()

        return explanation


class ExplanationDetailSerializer(serializers.ModelSerializer):
    uri_id = serializers.SlugRelatedField(read_only = True,
                                          slug_field = 'uri_id',)

    class Meta:
        model = Explanation
        fields = ['uri_id', 'type', 'title', 'created', 'updated', 'content']

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class ExplanationSimpleSerializer(serializers.ModelSerializer):
    uri_id = serializers.SlugRelatedField(read_only = True,
                                          slug_field = 'uri_id',)
    url = serializers.HyperlinkedIdentityField(
        view_name = 'explanation-detail',
        lookup_field = 'uri_id',)

    class Meta:
        model = Explanation
        fields = ['uri_id', 'type', 'title', 'url', 'content']
