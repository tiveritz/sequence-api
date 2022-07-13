import uuid

from django.db import models

from api.models.step import Step


class Explanation(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4)
    TYPE_CHOICES = (
        ('text', 'Text'),
        ('code', 'Code'),
    )
    type = models.CharField(max_length=32, choices=TYPE_CHOICES)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=128, blank=True)
    content = models.CharField(max_length=4096, blank=True)


class Image(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4)
    image = models.ImageField(blank=True, null=True)
    title = models.CharField(max_length=128, blank=True)
    caption = models.CharField(max_length=128, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @property
    def type(self):
        return 'image'


class Module(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(blank=False, null=False, default=uuid.uuid4)
    explanation = models.ForeignKey(
        Explanation,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    image = models.ForeignKey(
        Image,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'module'


class StepModule(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(blank=False, null=False, default=uuid.uuid4)
    step = models.ForeignKey(
        Step,
        on_delete=models.CASCADE,
    )
    pos = models.IntegerField()
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'step_module'
