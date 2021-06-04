from rest_framework import serializers
from .models import HowTo


class HowToSerializer(serializers.HyperlinkedModelSerializer): 
    class Meta:
        model = HowTo
        fields = ('uri_id', 'title', 'created', 'updated', 'url')

class HowToDetailSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = HowTo
        fields = ('id', 'title', 'created', 'updated', 'description',)