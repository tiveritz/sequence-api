import uuid

import pytest

from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_create_superstep(client, make_step):
    super = make_step()
    sub = make_step()

    url = reverse('api:superstep')

    payload = {'super': super.uuid, 'sub': sub.uuid}
    response = client.post(url, payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['super'] == str(super.uuid)
    assert response.data['sub'] == str(sub.uuid)
    assert response.data['pos'] == 0


@pytest.mark.django_db
def test_create_superstep_auto_pos(client, step, make_superstep):
    super = make_superstep(sub=1)

    url = reverse('api:superstep')

    payload = {'super': super.uuid, 'sub': step.uuid}
    response = client.post(url, payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['super'] == str(super.uuid)
    assert response.data['sub'] == str(step.uuid)
    assert response.data['pos'] == 1


@pytest.mark.django_db
def test_create_superstep_invalid_super_uuid_raises_error(client, make_step):
    super_uuid = uuid.uuid4()
    sub = make_step()

    url = reverse('api:superstep')

    payload = {'super': super_uuid, 'sub': sub.uuid}
    response = client.post(url, payload)

    assert response.status_code == status.HTTP_404_NOT_FOUND

    msg = 'Given superstep does not exist'
    assert str(response.data['detail']) == msg


@pytest.mark.django_db
def test_create_superstep_invalid_sub_uuid_raises_error(client, make_step):
    sub_uuid = uuid.uuid4()
    super = make_step()

    url = reverse('api:superstep')

    payload = {'super': super.uuid, 'sub': sub_uuid}
    response = client.post(url, payload)

    assert response.status_code == status.HTTP_404_NOT_FOUND

    msg = 'Given substep does not exist'
    assert str(response.data['detail']) == msg



# [ ] no pos -> auto end
# [ ] pos - valid
# [ ] 



'''

@pytest.mark.django_db
def test_link_unlink_substep_to_superstep(self, superstep, step):
    """
    Ensure client can link a Step to a Superstep, then delete it
    """
    # Link Step to Superstep
    url = reverse('sub-step', args=[superstep.api_id])
    data = {'api_id': step.api_id}
    self.api_client.post(url, data, format='json')

    # Check if Step was correctly linked
    url = reverse('step-detail', args=[superstep.api_id])
    response = self.api_client.get(url, format='json')

    msg = 'Step was not linked to Superstep correctly'
    response_api_id = response.data['substeps'][0]['api_id']
    assert response_api_id == str(step.api_id), msg

    # Unlink step
    url = reverse('super-detail',
                    args=[superstep.api_id, step.api_id])
    response = self.api_client.delete(url, format='json')

    # Check if Step was correctly unlinked
    url = reverse('step-detail', args=[superstep.api_id])
    response = self.api_client.get(url, format='json')

    msg = 'Step was not unlinked from Superstep correctly'
    assert len(response.data['substeps']) == 0, msg

@pytest.mark.django_db
def test_rearrange_substeps(self, superstep):
    """
    Ensure client can reorder substeps
    """
    # Create Substeps
    url = reverse('step-list')
    data = {'title': 'Substep1'}
    substep1 = self.api_client.post(url, data, format='json')
    data = {'title': 'Substep2'}
    substep2 = self.api_client.post(url, data, format='json')

    # Link Step to Superstep
    url = reverse('sub-step', args=[superstep.api_id])
    data = {'api_id': substep1.data['api_id']}
    self.api_client.post(url, data, format='json')
    data = {'api_id': substep2.data['api_id']}
    self.api_client.post(url, data, format='json')

    # Check initial order
    url = reverse('step-detail', args=[superstep.api_id])
    response = self.api_client.get(url, format='json')
    steps = response.data['substeps']

    msg = 'Initial step position is not ok'
    assert steps[0]['api_id'] == substep1.data['api_id'], msg
    assert steps[1]['api_id'] == substep2.data['api_id'], msg

    # Reorder
    url = reverse('sub-step', args=[superstep.api_id])
    data = {'method': 'order', 'old_index': 0, 'new_index': 1}
    response = self.api_client.patch(url, data, format='json')

    msg = 'Reorderung did not return 200'
    assert response.status_code == status.HTTP_200_OK, msg

    # Check new order
    url = reverse('step-detail', args=[superstep.api_id])
    response = self.api_client.get(url, format='json')
    steps = response.data['substeps']

    msg = 'Changed step position is not ok'
    assert steps[0]['api_id'] == substep2.data['api_id'], msg
    assert steps[1]['api_id'] == substep1.data['api_id'], msg

@pytest.mark.django_db
def test_delete_substep(self, superstep, step):
    """
    Ensure client can delete substeps
    """
    # Link Step to Superstep
    url = reverse('sub-step', args=[superstep.api_id])
    data = {'api_id': step.api_id}
    self.api_client.post(url, data, format='json')

    # Check if Step was correctly linked
    url = reverse('step-detail', args=[superstep.api_id])
    response = self.api_client.get(url, format='json').data

    msg = 'Substep was not linked to Superstep correctly'
    assert response['substeps'][0]['api_id'] == str(step.api_id), msg

    # Delete
    url = reverse('sub-step', args=[superstep.api_id])
    data = {'method': 'delete',
            'api_id': response['substeps'][0]['api_id']}
    response = self.api_client.patch(url, data, format='json')

    msg = 'Deleting Substep did not return 200'
    assert response.status_code == status.HTTP_200_OK, msg

    # Check if successfully deleted
    url = reverse('sub-step', args=[superstep.api_id])
    steps = self.api_client.get(url, format='json').data

    msg = 'Deleting Substep was not successfull'
    assert len(steps) == 0, msg

'''