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
    title = models.CharField(max_length=128, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    description = models.CharField(max_length=1024, blank=True)
    
    @property
    def steps(self):
        how_to_steps = HowToStep.objects.filter(how_to=self).order_by('pos')
        return [how_to_step.step for how_to_step in how_to_steps]
    
    def __str__(self):
        return f'{self.uri_id}, {self.title}'


class Step(AutoUriId, models.Model):
    uri_id = models.CharField(
        max_length=8,
        default='00000000',
        primary_key=True)
    title = models.CharField(max_length = 128, blank = True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    description = models.CharField(max_length = 1024, blank = True)

    @property
    def substeps(self):
        substeps = SuperStep.objects.filter(super=self).order_by('pos')
        return [substep.sub for substep in substeps]

    @property
    def modules(self):
        step_modules = StepModule.objects.filter(step = self).order_by('pos')
        modules = []

        for module in step_modules:
            if module.explanation:
                modules.append(module.explanation)
            elif module.image:
                modules.append(module.image)

        return modules

    @property
    def images(self):
        images = StepModule.objects.filter(step = self)
        return Image.objects.filter(stepexplanation__in = images).order_by('stepexplanation__pos')


    @property
    def is_super(self):
        return True if SuperStep.objects.filter(super_id = self.id).exists() else False

    def __str__(self):
        return f'{self.uri_id}, {self.title}'


class HowToStep(models.Model):
    how_to = models.ForeignKey(
        HowTo,
        on_delete = models.CASCADE
        )
    step = models.ForeignKey(
        Step,
        on_delete = models.CASCADE
        )
    pos = models.IntegerField()

    def __str__(self):
        return f'How To {self.how_to.uri_id} -> Step {self.step.uri_id}: pos {self.pos}'


class SuperStep(models.Model):
    super = models.ForeignKey(
        Step,
        on_delete = models.CASCADE,
        related_name = 'superstep'
        )
    sub = models.ForeignKey(
        Step,
        on_delete = models.CASCADE,
        related_name = 'substep'
        )
    pos = models.IntegerField()

    def __str__(self):
        return f'Super {self.super.uri_id} -> Step {self.sub.uri_id}: pos {self.pos}'


class Explanation(AutoUriId, models.Model):
    uri_id = models.CharField(
        max_length=8,
        default='00000000',
        primary_key=True)
    TYPE_CHOICES = (
        ('text', 'Text'),
        ('code', 'Code'),
    )
    type = models.CharField(max_length = 32, choices = TYPE_CHOICES)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length = 128, blank = True)
    content = models.CharField(max_length = 4096, blank = True)

    def __str__(self):
        return f'{self.uri_id}, {self.title}'


class Image(AutoUriId, models.Model):
    uri_id = models.CharField(
        max_length=8,
        default='00000000',
        primary_key=True)
    image = models.ImageField(blank=False, null=False)
    title = models.CharField(max_length = 128, blank = True)
    caption = models.CharField(max_length = 128, blank = True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @property
    def type(self):
        return 'image'

    def __str__(self):
        return f'{self.uri_id}, {self.title}'


class StepModule(models.Model):
    step = models.ForeignKey(
        Step,
        on_delete = models.CASCADE,
        )
    explanation = models.ForeignKey(
        Explanation,
        on_delete = models.CASCADE,
        blank=True,
        null=True
        )
    image = models.ForeignKey(
        Image,
        on_delete = models.CASCADE,
        blank=True,
        null=True
        )
    pos = models.IntegerField()

    def __str__(self):
        return f'Step {self.step.uri_id} -> Explanation {self.explanation.uri_id}: pos {self.pos}'
