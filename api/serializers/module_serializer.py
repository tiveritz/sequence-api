from rest_framework import serializers
from ..models import Explanation, Image
from .explanation_serializers import ExplanationDetailSerializer
from .media_serializers import ImageSerializer


class ModuleListSerializer(serializers.Serializer):
    @classmethod
    def get_serializer(cls, model):
        if model == Explanation:
            return ExplanationDetailSerializer
        elif model == Image:
            return ImageSerializer

    def to_representation(self, instance):
        serializer = self.get_serializer(instance.__class__)
        return serializer(instance, context=self.context).data
