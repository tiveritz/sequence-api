import uuid

from django.db import models

from api.base.choices import StepChoices


class Step(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(blank=False, null=False, default=uuid.uuid4)
    created = models.DateTimeField(blank=False, null=False, auto_now_add=True)
    updated = models.DateTimeField(blank=False, null=False, auto_now=True)
    title = models.CharField(max_length=128, blank=True, null=True)
    type = models.CharField(max_length=13,
                            blank=False,
                            null=False,
                            choices=StepChoices.choices,
                            default=StepChoices.STEP)

    def __str__(self):
        return f'{self.uuid}'

    @property
    def linked(self):
        linked_steps = LinkedStep.objects.filter(super=self).order_by('pos')
        return [linked_step.sub for linked_step in linked_steps]

    def get_parent_pks(self):
        try:
            linked_steps = LinkedStep.objects.filter(sub=self)
        except LinkedStep.DoesNotExist:
            return []

        parents = [li.super for li in linked_steps]

        parent_pks = []
        for parent in parents:
            parent_pks = parent.get_parent_pks()

        return [parent.pk for parent in parents] + parent_pks

    def update_type(self, type):
        self.type = type
        self.save()

    class Meta:
        db_table = 'step'


class LinkedStep(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(blank=False, null=False, default=uuid.uuid4)
    pos = models.IntegerField(blank=False, null=False, default=0)
    super = models.ForeignKey(Step,
                              blank=False,
                              null=False,
                              on_delete=models.CASCADE,
                              related_name='linked_step_super')
    sub = models.ForeignKey(Step,
                            blank=False,
                            null=False,
                            on_delete=models.CASCADE,
                            related_name='linked_step_sub')

    class Meta:
        db_table = 'linked_step'
