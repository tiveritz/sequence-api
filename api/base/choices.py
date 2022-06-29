from django.db.models import TextChoices


class StepChoices(TextChoices):
    STEP = "STEP"
    SEQUENCE_STEP = "SEQUENCE_STEP"
    DECISION_STEP = "DECISION_STEP"
