from django.db import models
from .functions.uri_id import generate_uri_id


class AutoUriId():
    def save(self, *args, **kwargs):
        if self.uri_id == '00000000':
            self.uri_id = generate_uri_id()
        super().save(*args, **kwargs)


class HowTo(AutoUriId, models.Model):
    uri_id = models.CharField(
        max_length=8,
        default='00000000',
        primary_key=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    publish_date = models.DateTimeField(null=True)
    title = models.CharField(max_length=128, blank=True)
    description = models.CharField(max_length=1024, blank=True)

    @property
    def steps(self):
        how_to_steps = HowToStep.objects.filter(how_to=self).order_by('pos')
        return [how_to_step.step for how_to_step in how_to_steps]

    def __str__(self):
        return f'{self.uri_id}, {self.title}'

    class Meta:
        db_table = 'howto'


class Step(AutoUriId, models.Model):
    uri_id = models.CharField(
        max_length=8,
        default='00000000',
        primary_key=True)
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
                    uri_id=module.explanation_id))
            elif module.image:
                modules.append(Image.objects.get(uri_id=module.image_id))

        return modules

    @property
    def images(self):
        modules = Module.objects.filter(step=self).order_by('pos')
        return Image.objects.filter(
            uri_id__in=modules.uri_id).order_by('module__pos')

    @property
    def is_super(self):
        return SuperStep.objects.filter(super=self).exists() or False

    @property
    def is_decision(self):
        return DecisionStep.objects.filter(super=self).exists() or False

    def __str__(self):
        return f'{self.uri_id}, {self.title}'

    class Meta:
        db_table = 'step'


class HowToStep(models.Model):
    how_to = models.ForeignKey(
        HowTo,
        on_delete=models.CASCADE
    )
    step = models.ForeignKey(
        Step,
        on_delete=models.CASCADE
    )
    pos = models.IntegerField()

    def __str__(self):
        return f'{self.how_to.uri_id} -> {self.step.uri_id}: {self.pos}'

    class Meta:
        db_table = 'howto_step'


class SuperStep(models.Model):
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
        return f'{self.super.uri_id} -> {self.sub.uri_id}: {self.pos}'

    class Meta:
        db_table = 'superstep'


class Explanation(AutoUriId, models.Model):
    uri_id = models.CharField(
        max_length=8,
        default='00000000',
        primary_key=True)
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
        return f'{self.uri_id}, {self.title}'


class Image(AutoUriId, models.Model):
    uri_id = models.CharField(
        max_length=8,
        default='00000000',
        primary_key=True)
    # Empty allowed because we have to create objects to name image with uri_id
    image = models.ImageField(blank=True, null=True)
    title = models.CharField(max_length=128, blank=True)
    caption = models.CharField(max_length=128, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @property
    def type(self):
        return 'image'

    def __str__(self):
        return f'{self.uri_id}, {self.title}'


class Module(models.Model):
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


class HowToGuide(AutoUriId, models.Model):
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
    uri_id = models.CharField(
        max_length=8,
        default='00000000',
        primary_key=True)
    howto_uri_id = models.CharField(
        max_length=8)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    space = models.CharField(
        max_length=3,
        choices=SPACES_CHOICES,
        default=TEST,
    )
    title = models.CharField(max_length=128)
    first = models.CharField(max_length=8)
    first_ref = models.CharField(max_length=8)
    steps = models.JSONField()

    class Meta:
        db_table = 'howto_guide'


class HowToGuideStep(models.Model):
    uri_id = models.CharField(
        max_length=8)
    ref_id = models.CharField(
        max_length=8,
        primary_key=True)
    howto = models.ForeignKey(
        HowToGuide,
        on_delete=models.CASCADE,
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    howto_title = models.CharField(max_length=128, blank=True)
    title = models.CharField(max_length=128)
    steps = models.JSONField()
    first = models.CharField(max_length=8)
    first_ref = models.CharField(max_length=8)
    previous = models.CharField(max_length=8, blank=True)
    previous_ref = models.CharField(max_length=8, blank=True)
    next = models.CharField(max_length=8, blank=True)
    next_ref = models.CharField(max_length=8, blank=True)
    content = models.CharField(max_length=4096, blank=True)

    class Meta:
        db_table = 'howto_guide_step'
