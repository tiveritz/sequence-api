import uuid

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


class SequenceGuide(models.Model):
    TEST = 'TST'
    PREVIEW = 'PRV'
    PUBLIC = 'PBL'
    PRIVATE = 'PRV'
    SPACES_CHOICES = [
        (TEST, 'test'),
        (PREVIEW, 'preview'),
        (PUBLIC, 'public'),
        (PRIVATE, 'private'),
    ]
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    space = models.CharField(
        max_length=3,
        choices=SPACES_CHOICES,
        default=TEST,
    )
    title = models.CharField(max_length=128)
    first = models.UUIDField()

    class Meta:
        db_table = 'sequence_guide'


class SequenceGuideStep(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4)
    sequence = models.ForeignKey(
        SequenceGuide,
        on_delete=models.CASCADE,
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    sequence_title = models.CharField(max_length=128, blank=True)
    title = models.CharField(max_length=128)
    decision_steps = models.CharField(max_length=2048, blank=True)
    first = models.UUIDField()
    previous = models.UUIDField(null=True)
    next = models.UUIDField(null=True)
    content = models.CharField(max_length=4096, blank=True)

    class Meta:
        db_table = 'sequence_guide_step'
