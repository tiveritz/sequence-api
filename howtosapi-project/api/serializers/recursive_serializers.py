from rest_framework import serializers


class RecursiveField(serializers.Serializer):
	# Source: https://programmersought.com/article/62131194762/
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context = self.context)
        return serializer.data
