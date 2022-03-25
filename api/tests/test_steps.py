import re
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


class TestStep():
    api_client = APIClient()

    @pytest.mark.django_db
    def test_create_step(self):
        """
        Ensure client can create a new Step
        """
        url = reverse('step-list')
        data = {'title': 'Create a Step'}
        response = self.api_client.post(url, data, format='json')

        msg = 'HTTP status return code is not 201'
        assert response.status_code == status.HTTP_201_CREATED, msg

        msg = 'Created data is not correct'
        assert response.data['title'] == data['title'], msg

    @pytest.mark.django_db
    def test_retrieve_step_by_id(self, step):
        """
        Ensure client can retreive a Step by Uri ID
        """
        url = reverse('step-detail', args=[step.api_id])
        response_get = self.api_client.get(url, format='json')

        msg = 'Retreiving Sequence by Uri ID failed'
        assert response_get.status_code == status.HTTP_200_OK, msg

        msg = 'Retreiving Sequence by Uri ID did not return the correct Sequence'
        assert response_get.data['title'] == step.title, msg

    @pytest.mark.django_db
    def test_update_step(self, step):
        """
        Ensure client can update Step
        """
        url = reverse('step-detail', args=[step.api_id])
        status_msg = 'HTTP status return code is not 200'
        data = {
            'title': 'New Title',
            'description': 'New Description',
        }

        for k, v in data.items():
            change_data = {k: v}
            response_patch = self.api_client.patch(
                url, change_data, format='json')

            assert response_patch.status_code == status.HTTP_200_OK, status_msg

            msg = f'Updating {k} failed'
            assert response_patch.data[k] == data[k], msg

    @pytest.mark.django_db
    def test_delete_step(self, step):
        """
        Ensure client can delete Step
        """
        url_delete = reverse('step-detail', args=[step.api_id])
        response_delete = self.api_client.delete(url_delete, format='json')

        msg = 'HTTP status return code is not 204'
        assert response_delete.status_code == status.HTTP_204_NO_CONTENT, msg

        url_get = reverse('step-detail', args=[step.api_id])
        response_get = self.api_client.get(url_get, format='json')
        msg = 'Step was not successfully deleted'
        assert response_get.status_code == status.HTTP_404_NOT_FOUND, msg

    @pytest.mark.django_db
    def test_forbidden_updates(self):
        """
        Ensure client can not change read only fields
        """
        url = reverse('step-list')
        data = {'title': 'Forbidden update'}
        response_post = self.api_client.post(url, data, format='json')

        url = reverse('step-detail', args=[response_post.data['api_id']])

        data = {
            'api_id': 'lolololo',
            'created': 'lol',
        }

        for k, v in data.items():
            forbidden_data = {k: v}
            response_patch = self.api_client.patch(
                url, forbidden_data, format='json')

            msg = f'Forbidden update on {k} was not blocked'
            assert response_post.data[k] == response_patch.data[k], msg


class TestSuperStep():
    api_client = APIClient()

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
