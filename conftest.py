import pytest
from api.models import HowTo, Step


@pytest.fixture()
def howto():
    return HowTo.objects.create(title='How To')


@pytest.fixture()
def superstep():
    return Step.objects.create(title='Superstep')


@pytest.fixture()
def step():
    return Step.objects.create(title='Step')
