import pytest
from api.models import Sequence, Step


@pytest.fixture()
def sequence():
    return Sequence.objects.create(title='Sequence')


@pytest.fixture()
def superstep():
    return Step.objects.create(title='Superstep')


@pytest.fixture()
def step():
    return Step.objects.create(title='Step')
