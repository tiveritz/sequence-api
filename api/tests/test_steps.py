import pytest

import uuid

from django.urls import reverse
from rest_framework import status

from api.models import Step


@pytest.mark.django_db
def test_get_step_by_uuid(client, step):
    kwargs = {'uuid': step.uuid}
    url = reverse('api:step', kwargs=kwargs)

    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['uuid'] == str(step.uuid)


@pytest.mark.django_db
def test_get_step_fields(client, step):
    kwargs = {'uuid': step.uuid}
    url = reverse('api:step', kwargs=kwargs)

    response = client.get(url)

    expected_fields = ['url',
                       'url_link_step',
                       'url_order_linked_steps',
                       'url_delete_linked_step',
                       'uuid',
                       'created',
                       'updated',
                       'title',
                       'type', ]
    received_fields = response.data.keys()

    assert set(expected_fields) == set(received_fields)


@pytest.mark.django_db
def test_create_empty_step(client):
    url = reverse('api:step-list')

    response = client.post(url)
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
@pytest.mark.parametrize('step_type',
                         ['DECISION', 'SEQUENCE', 'STEP', 'SUPER'])
def test_create_step(faker, client, step_type):
    url = reverse('api:step-list')
    title = faker.word()
    payload = {'title': title,
               'type': step_type}

    response = client.post(url, payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['title'] == title
    assert response.data['type'] == step_type


@pytest.mark.django_db
def test_create_step_invalid_type_raises_error(client):
    url = reverse('api:step-list')
    payload = {'title': '',
               'type': 'NOT_A_VALID_TYPE'}

    response = client.post(url, payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    msg = 'Given step type is not a valid step type'
    assert str(response.data['detail']) == msg


@pytest.mark.django_db
def test_create_step_ignores_uuid(client):
    url = reverse('api:step-list')
    step_uuid = str(uuid.uuid4())
    payload = {'uuid': step_uuid}

    response = client.post(url, payload)
    assert response.data['uuid'] != step_uuid


@pytest.mark.django_db
def test_update_step(client, step):
    kwargs = {'uuid': step.uuid}
    url = reverse('api:step', kwargs=kwargs)

    payload = {'title': 'new_title'}
    response = client.patch(url, payload)

    assert response.data['uuid'] == str(step.uuid)
    assert response.data['title'] == 'new_title'


@pytest.mark.django_db
def test_delete_step(client, step):
    kwargs = {'uuid': step.uuid}
    url = reverse('api:step', kwargs=kwargs)
    response = client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT

    with pytest.raises(Step.DoesNotExist):
        Step.objects.get(uuid=step.uuid)
