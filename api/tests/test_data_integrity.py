import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


class TestDataIntegrity():
    api_client = APIClient()

    @pytest.mark.django_db
    def test_forbid_howto_step_duplicate(self, howto, step):
        """
        Ensure client can not add a Substep to a How To more than once
        """
        url = reverse('how-to-step', args=[howto.uri_id])
        data = {'uri_id': step.uri_id}

        first_response = self.api_client.post(url, data, format='json')
        assert first_response.status_code == status.HTTP_201_CREATED

        second_response = self.api_client.post(url, data, format='json')
        msg = ('Adding duplicate Substeps in a How To did not return correct '
               'status code')
        assert second_response.status_code == status.HTTP_403_FORBIDDEN, msg

    @pytest.mark.django_db
    def test_forbid_superstep_step_duplicate(self, superstep, step):
        """
        Ensure client can not add a Substep to a Superstep more than once
        """
        url = reverse('sub-step', args=[superstep.uri_id])
        data = {'uri_id': step.uri_id}

        first_response = self.api_client.post(url, data, format='json')
        assert first_response.status_code == status.HTTP_201_CREATED

        second_response = self.api_client.post(url, data, format='json')
        msg = ('Adding duplicate Substeps in a Superstep did not return '
               'correct status code')
        assert second_response.status_code == status.HTTP_403_FORBIDDEN, msg

    @pytest.mark.django_db
    def test_forbid_circular_reference_parent(self):
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
