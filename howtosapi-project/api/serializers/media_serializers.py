from rest_framework import serializers
from ..models import Image


class ImageSerializer(serializers.ModelSerializer):
    class Meta():
        model = Image
        fields = ['uri_id', 'type', 'image', 'title', 'caption', 'created', 'updated']
