from django.db.models import TextChoices


class StepChoices(TextChoices):
    DECISION = 'DECISION'
    SEQUENCE = 'SEQUENCE'
    STEP = 'STEP'
    SUPER = 'SUPER'
