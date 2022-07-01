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
def superstep(make_superstep):
    return make_superstep()


@pytest.fixture
def make_supersteps(make_step):
    def _supersteps(super, sub=1):
        supersteps = []
        for pos in range(sub):
            sub = make_step()
            superstep = SuperStep.objects.create(super=super, sub=sub, pos=pos)
            supersteps.append(superstep)
        return supersteps
    return _supersteps
