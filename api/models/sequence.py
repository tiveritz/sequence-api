from django.db import models

from api.models.step import Step


class Sequence(models.Model):
    id = models.AutoField(primary_key=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    published = models.DateTimeField(null=True)
    step = models.OneToOneField(Step,
                                blank=False,
                                null=False,
                                on_delete=models.CASCADE,
                                related_name='step_sequence')

    class Meta:
        db_table = 'sequence'

    @property
    def uuid(self):
        return self.step.uuid
