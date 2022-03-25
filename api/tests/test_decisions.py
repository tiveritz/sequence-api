import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


class TestSuperStep():
    api_client = APIClient()

    @pytest.mark.django_db
    def test_rearrange_decisions(self, step):
        """
        Ensure client can reorder Decisions
        """
        # Create Decisions
        url = reverse('step-list')
        data = {'title': 'Decision1'}
        decision1 = self.api_client.post(url, data, format='json')
        data = {'title': 'Decision2'}
        decision2 = self.api_client.post(url, data, format='json')

        # Link Decision to Decisionstep
        url = reverse('decision-step', args=[step.api_id])
        data = {'api_id': decision1.data['api_id']}
        self.api_client.post(url, data, format='json')
        data = {'api_id': decision2.data['api_id']}
        self.api_client.post(url, data, format='json')

        # Check initial order
        url = reverse('step-detail', args=[step.api_id])
        response = self.api_client.get(url, format='json')
        steps = response.data['decisionsteps']

        msg = 'Initial decision position is not ok'
        assert steps[0]['api_id'] == decision1.data['api_id'], msg
        assert steps[1]['api_id'] == decision2.data['api_id'], msg

        # Reorder
        url = reverse('decision-step', args=[step.api_id])
        data = {'method': 'order', 'old_index': 0, 'new_index': 1}
        response = self.api_client.patch(url, data, format='json')

        msg = 'Reorderung did not return 200'
        assert response.status_code == status.HTTP_200_OK, msg

        # Check new order
        url = reverse('step-detail', args=[step.api_id])
        response = self.api_client.get(url, format='json')
        steps = response.data['decisionsteps']

        msg = 'Changed decision position is not ok'
        assert steps[0]['api_id'] == decision2.data['api_id'], msg
        assert steps[1]['api_id'] == decision1.data['api_id'], msg

    @pytest.mark.django_db
    def test_delete_decision(self, step):
        """
        Ensure client can delete Decisionsteps
        """
        # Create a Decision
        url = reverse('step-list')
        data = {'title': 'decisionstep to link'}
        decision = self.api_client.post(url, data, format='json')

        # Link Step to Decisionsteps
        url = reverse('decision-step', args=[step.api_id])
        data = {'api_id': decision.data['api_id']}
        self.api_client.post(url, data, format='json')

        # Check if Decision was correctly linked
        url = reverse('step-detail', args=[step.api_id])
        response = self.api_client.get(url, format='json').data

        msg = 'Decisionstep was not linked to Decisionsteps correctly'
        response_api_id = response['decisionsteps'][0]['api_id']
        data_api_id = decision.data['api_id']

        assert response_api_id == data_api_id, msg

        # Delete
        url = reverse('decision-step', args=[step.api_id])
        data = {'method': 'delete',
                'api_id': response['decisionsteps'][0]['api_id']}
        response = self.api_client.patch(url, data, format='json')

        msg = 'Deleting Decisionstep did not return 200'
        assert response.status_code == status.HTTP_200_OK, msg

        # Check if successfully deleted
        url = reverse('decision-step', args=[step.api_id])
        steps = self.api_client.get(url, format='json').data

        msg = 'Deleting Decisionstep was not successfull'
        assert len(steps) == 0, msg
