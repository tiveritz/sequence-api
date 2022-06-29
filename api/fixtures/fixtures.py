import pytest

from rest_framework.test import APIClient

from api.models import Sequence, Step, SuperStep
from api.base.choices import StepChoices


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def make_step():
    def _step():
        return Step.objects.create()
    return _step


@pytest.fixture
def step(make_step):
    return make_step()


@pytest.fixture
def sequence():
    step = Step.objects.create(type=StepChoices.SEQUENCE_STEP)
    return Sequence.objects.create(step=step)


@pytest.fixture
def make_superstep(make_step):
    def _superstep(sub=1):
        super = make_step()

        for pos in range(sub):
            sub = make_step()
            SuperStep.objects.create(super=super, sub=sub, pos=pos)
        return super
    return _superstep
