import pytest

import uuid

from django.urls import reverse
from rest_framework import status

from api.models import Step
from api.base.choices import StepChoices


@pytest.mark.django_db
def test_get_sequence_by_uuid(client, sequence):
    kwargs = {'uuid': sequence.uuid}
    url = reverse('api:sequence', kwargs=kwargs)

    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['uuid'] == str(sequence.uuid)


@pytest.mark.django_db
def test_get_sequence_fields(client, sequence):
    kwargs = {'uuid': sequence.uuid}
    url = reverse('api:sequence', kwargs=kwargs)

    response = client.get(url)

    expected_fields = ['url',
                       'uuid',
                       'created',
                       'updated',
                       'is_published',
                       'publish_date',
                       'step', ]
    received_fields = response.data.keys()

    assert set(expected_fields) == set(received_fields)
    assert response.data['step'] == str(sequence.step.uuid)


@pytest.mark.django_db
def test_create_sequence(client):
    url = reverse('api:sequence-list')
    response = client.post(url)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_sequence_step_type(client):
    url = reverse('api:sequence-list')
    response = client.post(url)

    step_uuid = response.data['step']
    step = Step.objects.get(uuid=step_uuid)

    assert step.type == StepChoices.SEQUENCE_STEP

@pytest.mark.django_db
def test_create_sequence_ignores_uuid(client):
    url = reverse('api:sequence-list')
    sequence_uuid = str(uuid.uuid4())
    payload = {'uuid': sequence_uuid}

    response = client.post(url, payload)
    assert response.data['uuid'] != sequence_uuid


@pytest.mark.django_db
def test_delete_sequence(client, sequence):
    kwargs = {'uuid': sequence.uuid}
    url = reverse('api:sequence', kwargs=kwargs)
    response = client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT

    with pytest.raises(Step.DoesNotExist):
        Step.objects.get(uuid=sequence.uuid)


@pytest.mark.django_db
def test_delete_non_existing_sequence_raises_error(client):
    kwargs = {'uuid': uuid.uuid4()}
    url = reverse('api:sequence', kwargs=kwargs)
    response = client.delete(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
