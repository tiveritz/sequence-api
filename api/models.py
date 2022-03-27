import uuid

from django.db import models


class Sequence(models.Model):
    id = models.AutoField(primary_key=True)
    api_id = models.UUIDField(default=uuid.uuid4)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    publish_date = models.DateTimeField(null=True)
    title = models.CharField(max_length=128, blank=True)
    description = models.CharField(max_length=1024, blank=True)

    @property
    def steps(self):
        sequence_steps = SequenceStep.objects.filter(sequence=self).order_by('pos')
        return [sequence_step.step for sequence_step in sequence_steps]

    def __str__(self):
        return f'{self.api_id}, {self.title}'

    class Meta:
        db_table = 'sequence'


class Step(models.Model):
    id = models.AutoField(primary_key=True)
    api_id = models.UUIDField(default=uuid.uuid4)
    title = models.CharField(max_length=128, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    description = models.CharField(max_length=1024, blank=True)

    @property
    def substeps(self):
        substeps = SuperStep.objects.filter(super=self).order_by('pos')
        return [substep.sub for substep in substeps]

    @property
    def decisionsteps(self):
        decisionsteps = DecisionStep.objects.filter(super=self).order_by('pos')
        return [step.decision for step in decisionsteps]

    @property
    def modules(self):
        step_modules = Module.objects.filter(
            stepmodule__step=self).order_by('stepmodule__pos')
        modules = []

        for module in step_modules:
            if module.explanation:
                modules.append(Explanation.objects.get(
                    id=module.explanation_id))
            elif module.image:
                modules.append(Image.objects.get(api_id=module.image_id))

        return modules

    @property
    def images(self):
        modules = Module.objects.filter(step=self).order_by('pos')
        return Image.objects.filter(
            api_id__in=modules.api_id).order_by('module__pos')

    @property
    def is_super(self):
        return SuperStep.objects.filter(super=self).exists() or False

    @property
    def is_decision(self):
        return DecisionStep.objects.filter(super=self).exists() or False

    def __str__(self):
        return f'{self.api_id}, {self.title}'

    class Meta:
        db_table = 'step'


class SequenceStep(models.Model):
    id = models.AutoField(primary_key=True)
    sequence = models.ForeignKey(
        Sequence,
        on_delete=models.CASCADE
    )
    step = models.ForeignKey(
        Step,
        on_delete=models.CASCADE
    )
    pos = models.IntegerField()

    def __str__(self):
        return f'{self.sequence.api_id} -> {self.step.api_id}: {self.pos}'

    class Meta:
        db_table = 'sequence_step'


class SuperStep(models.Model):
    id = models.AutoField(primary_key=True)
    pos = models.IntegerField()
    super = models.ForeignKey(
        Step,
        on_delete=models.CASCADE,
        related_name='superstep'
    )
    sub = models.ForeignKey(
        Step,
        on_delete=models.CASCADE,
        related_name='substep'
    )

    def __str__(self):
        return f'{self.super.api_id} -> {self.sub.api_id}: {self.pos}'

    class Meta:
        db_table = 'superstep'


class Explanation(models.Model):
    id = models.AutoField(primary_key=True)
    api_id = models.UUIDField(default=uuid.uuid4)
    TYPE_CHOICES = (
        ('text', 'Text'),
        ('code', 'Code'),
    )
    type = models.CharField(max_length=32, choices=TYPE_CHOICES)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=128, blank=True)
    content = models.CharField(max_length=4096, blank=True)

    def __str__(self):
        return f'{self.api_id}, {self.title}'


class Image(models.Model):
    id = models.AutoField(primary_key=True)
    api_id = models.UUIDField(default=uuid.uuid4)
    image = models.ImageField(blank=True, null=True)
    title = models.CharField(max_length=128, blank=True)
    caption = models.CharField(max_length=128, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @property
    def type(self):
        return 'image'

    def __str__(self):
        return f'{self.api_id}, {self.title}'


class Module(models.Model):
    id = models.AutoField(primary_key=True)
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


class DecisionStep(models.Model):
    id = models.AutoField(primary_key=True)
    pos = models.IntegerField()
    super = models.ForeignKey(
        Step,
        on_delete=models.CASCADE,
        related_name='superdecision'
    )
    decision = models.ForeignKey(
        Step,
        on_delete=models.CASCADE,
        related_name='decisionstep'
    )

    class Meta:
        db_table = 'decisionstep'


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
    api_id = models.UUIDField(default=uuid.uuid4)
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
    api_id = models.UUIDField(default=uuid.uuid4)
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
