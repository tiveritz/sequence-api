from rest_framework import serializers
from api.models.step import Image


class ImageSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='image-detail',
                                               lookup_field='api_id')

    class Meta():
        model = Image
        fields = ['api_id', 'type', 'image', 'title', 'caption', 'created',
                  'updated', 'url', ]


class ImageDetailSerializer(serializers.ModelSerializer):
    class Meta():
        model = Image
        fields = ['api_id', 'type', 'image', 'title', 'caption', 'created',
                  'updated', ]
