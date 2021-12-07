import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


class TestDataIntegrity():
    api_client = APIClient()

    @pytest.mark.django_db
    def test_forbidden_how_to_step_duplicate(self):
        """
        Ensure client can not add a Substep to a How To more than once
        """
        # Create a How To
        url = reverse('how-to-list')
        data = {'title': 'Linkable How To'}
        how_to = self.api_client.post(url, data, format='json')

        # Create a Substep
        url = reverse('step-list')
        data = {'title': 'Super'}
        step = self.api_client.post(url, data, format='json')

        # Link Step to How To
        url = reverse('how-to-step', args=[how_to.data['uri_id']])
        data_2 = {'uri_id': step.data['uri_id']}
        self.api_client.post(url, data_2, format='json')

        # Try to link the step a second time
        url = reverse('how-to-step', args=[how_to.data['uri_id']])
        data_3 = {'uri_id': step.data['uri_id']}
        response = self.api_client.post(url, data_3, format='json')

        msg = ('Adding duplicate Substeps in a How To did not return correct '
               'status code')
        assert response.status_code == status.HTTP_403_FORBIDDEN, msg

    @pytest.mark.django_db
    def test_forbidden_step_duplicate(self):
        """
        Ensure client can not add a Substep to a Superstep more than once
        """
        # Create a Superstep
        url = reverse('step-list')
        data = {'title': 'Super'}
        superstep = self.api_client.post(url, data, format='json')

        # Create a Substep
        url = reverse('step-list')
        data = {'title': 'Super'}
        substep = self.api_client.post(url, data, format='json')

        # Link Step to Superstep
        url = reverse('sub-step', args=[superstep.data['uri_id']])
        data = {'uri_id': substep.data['uri_id']}
        self.api_client.post(url, data, format='json')

        # Try to link the step a second time
        url = reverse('sub-step', args=[superstep.data['uri_id']])
        data = {'uri_id': substep.data['uri_id']}
        response = self.api_client.post(url, data, format='json')

        msg = ('Adding duplicate Substeps in a Superstep did not return '
               'correct status code')
        assert response.status_code == status.HTTP_403_FORBIDDEN, msg

    @pytest.mark.django_db
    def test_forbidden_circular_reference_parent(self):
        """
        Ensure client can not add a Substep to a Superstep that has itself or
        any of its children already added
        """
        # Define Tree
        #
        # a       d     e
        # L b     L b   L f
        #   L c           L b
        #                   L c

        # Create Steps
        steps = {
            'a': None,
            'b': None,
            'c': None,
            'd': None,
            'e': None,
            'f': None,
        }

        url = reverse('step-list')
        for stepname in steps:
            data = {'title': stepname}
            steps[stepname] = self.api_client.post(url, data, format='json')

        # Link Steps
        links = [
            (steps['b'], steps['a']),
            (steps['c'], steps['b']),
            (steps['b'], steps['d']),
            (steps['f'], steps['e']),
            (steps['b'], steps['f']),
        ]

        for link in links:
            url = reverse('sub-step', args=[link[0].data['uri_id']])
            data = {'uri_id': link[1].data['uri_id']}
            self.api_client.post(url, data, format='json')

        # Try to link c to e -> conflict c (is substep of e)
        url = reverse('sub-step', args=[steps['c'].data['uri_id']])
        data = {'uri_id': steps['e'].data['uri_id']}
        response = self.api_client.post(url, data, format='json')

        msg = 'Adding forbidden circular reference was not blocked'
        assert response.status_code == status.HTTP_403_FORBIDDEN, msg

        # Try to link e to c -> conflict e (has c and b as substep)
        url = reverse('sub-step', args=[steps['c'].data['uri_id']])
        data = {'uri_id': steps['e'].data['uri_id']}
        response = self.api_client.post(url, data, format='json')

        msg = 'Adding forbidden circular reference was not blocked'
        assert response.status_code == status.HTTP_403_FORBIDDEN, msg
