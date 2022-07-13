import uuid

from django.db import models

from api.models.step import Step


class Sequence(models.Model):
    id = models.AutoField(primary_key=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    published = models.DateTimeField(null=True)
    step = models.OneToOneField(
        Step,
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name='step_sequence')

    class Meta:
        db_table = 'sequence'

    @property
    def uuid(self):
        return self.step.uuid


class PublishedSequence(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4)
    published = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=128)
    first = models.UUIDField()
    sequence = models.ForeignKey(
        Sequence,
        blank=False,
        null=False,
        on_delete=models.PROTECT,
        related_name='sequence_published_sequence')


class PublishedStep(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4)
    title = models.CharField(max_length=128)

    first = models.UUIDField()
    previous = models.UUIDField(null=True)
    next = models.UUIDField(null=True)

    published_sequence = models.ForeignKey(
        PublishedSequence,
        blank=False,
        null=False,
        on_delete=models.PROTECT,
        related_name='published_step_published_sequence')
    sequence = models.ForeignKey(
        Sequence,
        blank=False,
        null=False,
        on_delete=models.PROTECT,
        related_name='published_step_sequence')
