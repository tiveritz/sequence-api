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
                       'published',
                       'step',
                       'title',
                       'linked']
    received_fields = response.data.keys()

    assert set(expected_fields) == set(received_fields)
    assert response.data['step'] == str(sequence.step.uuid)


@pytest.mark.django_db
def test_create_sequence(client):
    url = reverse('api:sequence-list')
    response = client.post(url)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_add_sequence_creates_step(client):
    url = reverse('api:sequence-list')
    response = client.post(url)

    assert response.data['uuid'] is not None

    step_uuid = response.data['step']
    step = Step.objects.get(uuid=step_uuid)
    assert step.type == StepChoices.SEQUENCE


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


@pytest.mark.django_db
def test_sequence_detail_shows_linked_steps(client, sequence,
                                            make_linked_steps):
    linked_step = make_linked_steps(super=sequence.step, sub=1)[0]

    kwargs = {'uuid': sequence.uuid}
    url = reverse('api:sequence', kwargs=kwargs)

    response = client.get(url)

    expected_fields = ['url_link_step',
                       'url_linkable_steps',
                       'url_order_linked_steps',
                       'url_delete_linked_step',
                       'uuid',
                       'created',
                       'updated',
                       'title',
                       'type',
                       'linked']

    received_fields = response.data['linked'][0].keys()

    assert set(expected_fields) == set(received_fields)
    assert response.data['linked'][0]['uuid'] == str(linked_step.sub.uuid)
