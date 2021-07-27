from rest_framework import serializers
from ..models import Image
from ..functions.uri_id_generator import generate


class ImageSerializer(serializers.ModelSerializer):
    class Meta():
        model = Image
        fields = ['uri_id', 'type', 'image', 'title', 'caption', 'created', 'updated']
