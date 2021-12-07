from rest_framework import serializers
from ..models import Image


class ImageSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='image-detail',
                                               lookup_field='uri_id')

    class Meta():
        model = Image
        fields = ['uri_id', 'type', 'image', 'title', 'caption', 'created',
                  'updated', 'url', ]


class ImageDetailSerializer(serializers.ModelSerializer):
    class Meta():
        model = Image
        fields = ['uri_id', 'type', 'image', 'title', 'caption', 'created',
                  'updated', ]
