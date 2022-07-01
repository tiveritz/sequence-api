from django.db.models import Max
from rest_framework.serializers import (CharField,
                                        HyperlinkedIdentityField,
                                        IntegerField,
                                        ModelSerializer,
                                        UUIDField)

from api.base.choices import StepChoices
from api.base.exceptions import NotAValidStepType
from api.models import Step, SuperStep


class StepSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(view_name='api:step', lookup_field='uuid')
    url_add_substep = HyperlinkedIdentityField(view_name='api:step-add',
                                               lookup_field='uuid')
    url_order_substeps = HyperlinkedIdentityField(view_name='api:step-order',
                                                  lookup_field='uuid')
    url_delete_substep = HyperlinkedIdentityField(view_name='api:step-delete',
                                                  lookup_field='uuid')

    title = CharField(required=False)
    type = CharField(required=False)

    class Meta:
        model = Step
        exclude = ['id']
        read_only_fields = ('uuid', 'created', 'updated')

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


class SubstepAddSerializer(ModelSerializer):
    super = UUIDField(read_only=True)
    sub = UUIDField()
    pos = IntegerField(read_only=True)

    class Meta:
        model = SuperStep
        exclude = ['id']

    def create(self, validated_data):
        super = Step.objects.get(uuid=self.context['uuid'])
        sub = Step.objects.get(uuid=validated_data['sub'])

        max_pos = SuperStep.objects.filter(super=super) \
                                   .aggregate(Max('pos'))['pos__max']
        new_pos = 0 if max_pos is None else max_pos + 1
        return SuperStep.objects.create(super=super, sub=sub, pos=new_pos)
