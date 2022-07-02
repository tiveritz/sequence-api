import pytest

from rest_framework.test import APIClient

from api.models import Sequence, Step, LinkedStep
from api.base.choices import StepChoices


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def make_step():
    def _step(type=None):
        return Step.objects.create(type=type or StepChoices.STEP)
    return _step


@pytest.fixture
def step(make_step):
    return make_step()


@pytest.fixture
def sequence():
    step = Step.objects.create(type=StepChoices.SEQUENCE)
    return Sequence.objects.create(step=step)


@pytest.fixture
def make_linked_steps(make_step):
    def _linked_steps(super, sub=1):
        super.type = StepChoices.SUPER
        super.save()

        linked_steps = []
        for pos in range(sub):
            sub = make_step()
            linked_step = LinkedStep.objects.create(super=super,
                                                    sub=sub,
                                                    pos=pos)
            linked_steps.append(linked_step)
        return linked_steps
    return _linked_steps
