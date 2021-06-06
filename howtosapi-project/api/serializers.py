from rest_framework import serializers
from .models import HowTo, HowToUriId
from api.uri_id_generator import generate


class HowToSerializer(serializers.HyperlinkedModelSerializer): 
    url = serializers.HyperlinkedIdentityField(
        view_name = 'how-to-detail',
    )

    class Meta:
        model = HowTo
        fields = ('id', 'uri_id', 'title', 'created', 'updated', 'url')
    
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

class HowToDetailSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = HowTo
        fields = ('id', 'uri_id', 'title', 'created', 'updated', 'description')
    
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
