import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


class TestSuperStep():
    api_client = APIClient()

    @pytest.mark.django_db
    def test_rearrange_decisions(self):
        """
        Ensure client can reorder Decisions
        """
        # Create a Decisionstep
        url = reverse('step-list')
        data = {'title': 'Decisionstep to link'}
        decisionstep = self.api_client.post(url, data, format='json')

        # Create Decisions
        url = reverse('step-list')
        data = {'title': 'Decision1'}
        decision1 = self.api_client.post(url, data, format='json')
        data = {'title': 'Decision2'}
        decision2 = self.api_client.post(url, data, format='json')

        # Link Decision to Decisionstep
        url = reverse('decision-step', args=[decisionstep.data['uri_id']])
        data = {'uri_id': decision1.data['uri_id']}
        self.api_client.post(url, data, format='json')
        data = {'uri_id': decision2.data['uri_id']}
        self.api_client.post(url, data, format='json')

        # Check initial order
        url = reverse('step-detail', args=[decisionstep.data['uri_id']])
        response = self.api_client.get(url, format='json')
        steps = response.data['decisionsteps']

        msg = 'Initial decision position is not ok'
        assert steps[0]['uri_id'] == decision1.data['uri_id'], msg
        assert steps[1]['uri_id'] == decision2.data['uri_id'], msg

        # Reorder
        url = reverse('decision-step', args=[decisionstep.data['uri_id']])
        data = {'method': 'order', 'old_index': 0, 'new_index': 1}
        response = self.api_client.patch(url, data, format='json')

        msg = 'Reorderung did not return 200'
        assert response.status_code == status.HTTP_200_OK, msg

        # Check new order
        url = reverse('step-detail', args=[decisionstep.data['uri_id']])
        response = self.api_client.get(url, format='json')
        steps = response.data['decisionsteps']

        msg = 'Changed decision position is not ok'
        assert steps[0]['uri_id'] == decision2.data['uri_id'], msg
        assert steps[1]['uri_id'] == decision1.data['uri_id'], msg

    @pytest.mark.django_db
    def test_delete_decision(self):
        """
        Ensure client can delete Decisionsteps
        """
        # Create a Decisionsteps
        url = reverse('step-list')
        data = {'title': 'decisionsteps to link'}
        decisionsteps = self.api_client.post(url, data, format='json')

        # Create a Decisionstep
        url = reverse('step-list')
        data = {'title': 'decisionstep to link'}
        decisionstep = self.api_client.post(url, data, format='json')

        # Link Step to Decisionsteps
        url = reverse('decision-step', args=[decisionsteps.data['uri_id']])
        data = {'uri_id': decisionstep.data['uri_id']}
        self.api_client.post(url, data, format='json')

        # Check if Decision was correctly linked
        url = reverse('step-detail', args=[decisionsteps.data['uri_id']])
        response = self.api_client.get(url, format='json').data

        msg = 'Decisionstep was not linked to Decisionsteps correctly'
        response_uri_id = response['decisionsteps'][0]['uri_id']
        data_uri_id = decisionstep.data['uri_id']

        assert response_uri_id == data_uri_id, msg

        # Delete
        url = reverse('decision-step', args=[decisionsteps.data['uri_id']])
        data = {'method': 'delete',
                'uri_id': response['decisionsteps'][0]['uri_id']}
        response = self.api_client.patch(url, data, format='json')

        msg = 'Deleting Decisionstep did not return 200'
        assert response.status_code == status.HTTP_200_OK, msg

        # Check if successfully deleted
        url = reverse('decision-step', args=[decisionsteps.data['uri_id']])
        steps = self.api_client.get(url, format='json').data

        msg = 'Deleting Decisionstep was not successfull'
        assert len(steps) == 0, msg
