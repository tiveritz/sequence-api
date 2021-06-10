from django.db import models


class HowTo(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length = 128, blank = True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    description = models.CharField(max_length = 1024, blank = True)

    @property
    def uri_id(self):
        return HowToUriId.objects.get(how_to_id = self)
    
    @property
    def steps(self):
        how_to_steps = HowToStep.objects.filter(how_to_id = self.id)
        step_ids = how_to_steps.values_list('step_id', flat = True)
        return Step.objects.filter(id__in = step_ids).order_by('step__pos')
    
    def __str__(self):
        return f'{self.title}'
    
    class Meta:
        verbose_name = 'How To\''


class HowToUriId(models.Model):
    id = models.BigAutoField(primary_key=True)
    how_to_id = models.OneToOneField(
        HowTo,
        on_delete = models.CASCADE
        )
    uri_id = models.CharField(max_length = 8)

    def __str__(self):
        return f'{self.uri_id}'

    class Meta:
        verbose_name = 'How To Uri Id\''


class Step(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length = 128, blank = True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    description = models.CharField(max_length = 1024, blank = True)

    @property
    def uri_id(self):
        return StepUriId.objects.get(step_id = self)

    @property
    def substeps(self):
        substeps = Super.objects.filter(super_id = self.id)
        step_ids = substeps.values_list('step_id', flat = True)
        return Step.objects.filter(id__in = step_ids).order_by('substep__pos')

    def __str__(self):
        return f'{self.title}'

class StepUriId(models.Model):
    id = models.BigAutoField(primary_key=True)
    step_id = models.OneToOneField(
        Step,
        on_delete = models.CASCADE
        )
    uri_id = models.CharField(max_length = 8)

    class Meta:
        verbose_name = 'Step Uri Id\''

    def __str__(self):
        return f'{self.uri_id}'

class HowToStep(models.Model):
    how_to_id = models.ForeignKey(
        HowTo,
        on_delete = models.CASCADE,
        related_name = 'how_to'
        )
    step_id = models.ForeignKey(
        Step,
        on_delete = models.CASCADE,
        related_name = 'step'
        )
    pos = models.IntegerField()

    class Meta:
        verbose_name = 'How To\'s linked Step'

    def __str__(self):
        return f'How To {self.how_to_id.uri_id} -> Step {self.step_id.uri_id}: pos {self.pos}'

class Super(models.Model):
    super_id = models.ForeignKey(
        Step,
        on_delete = models.CASCADE,
        related_name = 'superstep'
        )
    step_id = models.ForeignKey(
        Step,
        on_delete = models.CASCADE,
        related_name = 'substep'
        )
    pos = models.IntegerField()

    class Meta:
        verbose_name = 'Superstep'

    def __str__(self):
        return f'Super {self.super_id.uri_id} -> Step {self.step_id.uri_id}: pos {self.pos}'