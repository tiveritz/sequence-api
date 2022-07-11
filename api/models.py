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
