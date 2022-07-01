from rest_framework import serializers
from ..models import Explanation


class ExplanationSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='explanation-detail',
        lookup_field='api_id',)

    class Meta:
        model = Explanation
        fields = ['api_id', 'type', 'title', 'created', 'updated', 'url']

    def create(self, validated_data):
        return Explanation.objects.create(**validated_data)


class ExplanationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Explanation
        fields = ['api_id', 'type', 'title', 'created', 'updated', 'content']
        read_only_fields = ['api_id', 'created', 'updated', ]

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class ExplanationSimpleSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='explanation-detail',
        lookup_field='api_id',)

    class Meta:
        model = Explanation
        fields = ['api_id', 'type', 'title', 'url', 'content']
