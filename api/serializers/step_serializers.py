from django.db.models import Max
from rest_framework.serializers import (CharField,
                                        HyperlinkedIdentityField,
                                        IntegerField,
                                        ModelSerializer,
                                        UUIDField)

from api.base.choices import StepChoices
from api.base.exceptions import NotAValidStepType
from api.models import Step, LinkedStep
from api.serializers.recursive_serializers import RecursiveSerializer


class StepSerializer(ModelSerializer):
    url_linkable_steps = \
        HyperlinkedIdentityField(view_name='api:step-linkable',
                                 lookup_field='uuid')
    url_link_step = HyperlinkedIdentityField(view_name='api:step-link',
                                             lookup_field='uuid')
    url_order_linked_steps = \
        HyperlinkedIdentityField(view_name='api:linked-step-order',
                                 lookup_field='uuid')
    url_delete_linked_step = \
        HyperlinkedIdentityField(view_name='api:linked-step-delete',
                                 lookup_field='uuid')

    title = CharField(read_only=True)
    type = CharField(read_only=True)
    linked = RecursiveSerializer(many=True)

    class Meta:
        model = Step
        exclude = ['id']
        read_only_fields = ('url_link_step', 'url_order_linked_steps',
                            'url_delete_linked_step', 'uuid', 'created',
                            'updated', 'linked', 'url_linkable_steps')

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class StepsSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(view_name='api:step', lookup_field='uuid')

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


class LinkStepSerializer(ModelSerializer):
    super = UUIDField(read_only=True)
    sub = UUIDField()
    pos = IntegerField(read_only=True)

    class Meta:
        model = LinkedStep
        exclude = ['id']

    def create(self, validated_data):
        super = Step.objects.get(uuid=self.context['uuid'])
        sub = Step.objects.get(uuid=validated_data['sub'])

        max_pos = LinkedStep.objects.filter(super=super) \
                                    .aggregate(Max('pos'))['pos__max']
        new_pos = 0 if max_pos is None else max_pos + 1
        linked_step = LinkedStep.objects.create(super=super,
                                                sub=sub,
                                                pos=new_pos)

        if super.type != StepChoices.SEQUENCE:
            super.update_type(StepChoices.SUPER)

        return linked_step
