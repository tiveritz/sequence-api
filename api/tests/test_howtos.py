import re
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


class TestHowTo():
    api_client = APIClient()

    @pytest.mark.django_db
    def test_create_how_to(self):
        """
        Ensure client can create a new How To
        """
        url = reverse('how-to-list')
        data = {'title': 'How to Create a How To'}
        response = self.api_client.post(url, data, format='json')

        msg = 'HTTP status return code is not 201'
        assert response.status_code == status.HTTP_201_CREATED, msg

        msg = 'Created title is not correct'
        assert response.data['title'] == data['title'], msg

        msg = 'Created Uri ID is not correct'
        # Matches any word with lower letters, numbers with a exact length of
        # 8 characters
        pattern = re.compile(r'^[a-z0-9]{8}$')
        is_match = re.match(pattern, str(response.data['uri_id'])) or False
        assert is_match, msg

    @pytest.mark.django_db
    def test_retrieve_how_to_by_id(self):
        """
        Ensure client can retreive a How To by Uri ID
        """
        url = reverse('how-to-list')
        data = {'title': 'test title'}
        response_post = self.api_client.post(url, data, format='json')

        url = reverse('how-to-detail', args=[response_post.data['uri_id']])
        response_get = self.api_client.get(url, format='json')

        msg = 'Retreiving How To by Uri ID failed'
        assert response_get.status_code == status.HTTP_200_OK, msg

        msg = 'Retreiving How To by Uri ID did not return the correct how to'
        assert response_get.data['title'] == data['title'], msg

    @pytest.mark.django_db
    def test_update_how_to(self):
        """
        Ensure client can update How To
        """
        url = reverse('how-to-list')
        data = {'title': 'Update a How To'}
        response_post = self.api_client.post(url, data, format='json')

        url = reverse('how-to-detail', args=[response_post.data['uri_id']])
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
    def test_delete_how_to(self):
        """
        Ensure client can delete How To
        """
        url_post = reverse('how-to-list')
        data = {'title': 'How To'}
        response_post = self.api_client.post(url_post, data, format='json')

        url_delete = reverse(
            'how-to-detail', args=[response_post.data['uri_id']])
        response_delete = self.api_client.delete(url_delete, format='json')

        msg = 'HTTP status return code is not 204'
        assert response_delete.status_code == status.HTTP_204_NO_CONTENT, msg

        url_get = reverse('how-to-detail', args=[response_post.data['uri_id']])
        response_get = self.api_client.get(url_get, data, format='json')
        msg = 'How To was not successfully deleted'
        assert response_get.status_code == status.HTTP_404_NOT_FOUND, msg

    @pytest.mark.django_db
    def test_forbidden_updates(self):
        """
        Ensure client can not change read only fields
        """
        url = reverse('how-to-list')
        data = {'title': 'Forbidden update'}
        response_post = self.api_client.post(url, data, format='json')

        url = reverse('how-to-detail', args=[response_post.data['uri_id']])

        data = {
            'uri_id': 'lolololo',
            'created': 'lol',
        }

        for k, v in data.items():
            forbidden_data = {k: v}
            response_patch = self.api_client.patch(
                url, forbidden_data, format='json')

            msg = f'Forbidden update on {k} was not blocked'
            assert response_post.data[k] == response_patch.data[k], msg


class TestHowToStep():
    api_client = APIClient()

    @pytest.mark.django_db
    def test_link_unlink_step_to_how_to(self):
        """
        Ensure client can link a Step to a How to, then delete it
        """
        # Create a How To
        url = reverse('how-to-list')
        data = {'title': 'Linkable How To'}
        how_to = self.api_client.post(url, data, format='json')

        # Create a Step
        url = reverse('step-list')
        data = {'title': 'Step to link'}
        step = self.api_client.post(url, data, format='json')

        # Link Step to How To
        url = reverse('how-to-step', args=[how_to.data['uri_id']])
        data = {'uri_id': step.data['uri_id']}
        self.api_client.post(url, data, format='json')

        # Check if Step was correctly linked
        url = reverse('how-to-detail', args=[how_to.data['uri_id']])
        response = self.api_client.get(url, format='json')

        msg = 'Step was not linked to How To correctly'
        assert response.data['steps'][0]['uri_id'] == step.data['uri_id'], msg

        # Unlink step
        url = reverse('how-to-step-detail',
                      args=[how_to.data['uri_id'], step.data['uri_id']])
        response = self.api_client.delete(url, format='json')

        # Check if Step was correctly unlinked
        url = reverse('how-to-detail', args=[how_to.data['uri_id']])
        response = self.api_client.get(url, format='json')

        msg = 'Step was not unlinked from How To correctly'
        assert len(response.data['steps']) == 0, msg

    @pytest.mark.django_db
    def test_rearrange_substeps(self):
        """
        Ensure client can reorder substeps
        """
        # Create a Superstep
        url = reverse('how-to-list')
        data = {'title': 'Linkable How To'}
        how_to = self.api_client.post(url, data, format='json')

        # Create Substeps
        url = reverse('step-list')
        data = {'title': 'Substep1'}
        substep1 = self.api_client.post(url, data, format='json')
        data = {'title': 'Substep2'}
        substep2 = self.api_client.post(url, data, format='json')

        # Link Step to Superstep
        url = reverse('how-to-step', args=[how_to.data['uri_id']])
        data = {'uri_id': substep1.data['uri_id']}
        self.api_client.post(url, data, format='json')
        data = {'uri_id': substep2.data['uri_id']}
        self.api_client.post(url, data, format='json')

        # Check initial order
        url = reverse('how-to-detail', args=[how_to.data['uri_id']])
        response = self.api_client.get(url, format='json')
        steps = response.data['steps']

        msg = 'Initial step position is not ok'
        assert steps[0]['uri_id'] == substep1.data['uri_id'], msg
        assert steps[1]['uri_id'] == substep2.data['uri_id'], msg

        # Reorder
        url = reverse('how-to-step', args=[how_to.data['uri_id']])
        data = {'method': 'order', 'old_index': 0, 'new_index': 1}
        response = self.api_client.patch(url, data, format='json')

        msg = 'Reorderung Substep did not return 200'
        assert response.status_code == status.HTTP_200_OK, msg

        # Check new order
        url = reverse('how-to-step', args=[how_to.data['uri_id']])
        steps = self.api_client.get(url, format='json').data

        msg = 'Changed step position is not ok'
        assert steps[0]['uri_id'] == substep2.data['uri_id'], msg
        assert steps[1]['uri_id'] == substep1.data['uri_id'], msg

    @pytest.mark.django_db
    def test_delete_substep(self):
        """
        Ensure client can delete substeps
        """
        # Create a How To
        url = reverse('how-to-list')
        data = {'title': 'Linkable How To'}
        how_to = self.api_client.post(url, data, format='json')

        # Create a Step
        url = reverse('step-list')
        data = {'title': 'Step to link'}
        step = self.api_client.post(url, data, format='json')

        # Link Step to How To
        url = reverse('how-to-step', args=[how_to.data['uri_id']])
        data = {'uri_id': step.data['uri_id']}
        self.api_client.post(url, data, format='json')

        # Check if Step was correctly linked
        url = reverse('how-to-detail', args=[how_to.data['uri_id']])
        response = self.api_client.get(url, format='json').data

        msg = 'Step was not linked to How To correctly'
        assert response['steps'][0]['uri_id'] == step.data['uri_id'], msg

        # Delete
        url = reverse('how-to-step', args=[how_to.data['uri_id']])
        data = {'method': 'delete', 'uri_id': response['steps'][0]['uri_id']}
        response = self.api_client.patch(url, data, format='json')

        msg = 'Deleting Substep did not return 200'
        assert response.status_code == status.HTTP_200_OK, msg

        # Check if successfully deleted
        url = reverse('how-to-step', args=[how_to.data['uri_id']])
        steps = self.api_client.get(url, format='json').data

        msg = 'Deleting Substep was not successfull'
        assert len(steps) == 0, msg
