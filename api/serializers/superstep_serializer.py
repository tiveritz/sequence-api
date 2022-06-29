from django.db.models import Max
from rest_framework.serializers import ModelSerializer, UUIDField, IntegerField

from api.models import SuperStep, Step
from api.base.exceptions import SubStepDoesNotExist, SuperStepDoesNotExist


class SuperStepSerializer(ModelSerializer):
    super = UUIDField(source='super.uuid')
    sub = UUIDField(source='sub.uuid')
    pos = IntegerField(required=False)

    class Meta:
        model = SuperStep
        exclude = ['id']

    def create(self, validated_data):
        try:
            super = Step.objects.get(uuid=validated_data['super']['uuid'])
        except Step.DoesNotExist:
            raise SuperStepDoesNotExist

        try:
            sub = Step.objects.get(uuid=validated_data['sub']['uuid'])
        except Step.DoesNotExist:
            raise SubStepDoesNotExist

        max_pos = SuperStep.objects.filter(super=super).aggregate(Max('pos'))['pos__max']
        new_pos = 0 if max_pos is None else max_pos + 1
        return SuperStep.objects.create(super=super, sub=sub, pos=new_pos)



'''
    def validate_type(self, value):
        if value not in StepChoices:
            raise NotAValidStepType
        return value

    def create(self, validated_data):
        return Step.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
'''