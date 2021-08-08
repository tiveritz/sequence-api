import re
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class StepTest(APITestCase):
    def test_create_step(self):
        """
        Ensure client can create a new Step
        """
        url = reverse('step-list')
        data = {'title' : 'How to Create a Step'}
        response = self.client.post(url, data, format = 'json')

        msg = 'HTTP status return code is not 201'
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg)

        msg = 'Created data is not correct'  
        self.assertEqual(response.data['title'], data['title'], msg)

        msg = 'Uri ID was not created correctly'
        # Matches any word with lower letters, numbers with a exact length of
        # 8 characters
        pattern = re.compile(r'^[a-z0-9]{8}$')
        is_match = re.match(pattern, str(response.data['uri_id'])) or False
        self.assertTrue(is_match, msg)


    def test_retrieve_step_by_id(self):
        """
        Ensure client can retreive a Step by Uri ID
        """
        url = reverse('step-list')
        data = {'title' : 'new'}
        response_post = self.client.post(url, data, format = 'json')

        url = reverse('step-detail', args = [response_post.data['uri_id']])
        response_get = self.client.get(url, format = 'json')

        msg = 'Retreiving How To by Uri ID failed'  
        self.assertEqual(response_get.status_code, status.HTTP_200_OK, msg)      
        
        msg = 'Retreiving How To by Uri ID did not return the correct how to'  
        self.assertEqual(response_get.data['title'], data['title'], msg)

    def test_update_step(self):
        """
        Ensure client can update Step
        """
        url = reverse('step-list')
        data = {'title' : 'Update a Step'}
        response_post = self.client.post(url, data, format = 'json')
        
        url = reverse('step-detail', args = [response_post.data['uri_id']])
        status_msg = 'HTTP status return code is not 200'
        data = {
            'title' : 'New Title',
            'description' : 'New Description',
        }

        for k, v in data.items():
            change_data = {k : v}
            response_patch = self.client.patch(url, change_data, format = 'json')

            self.assertEqual(response_patch.status_code, status.HTTP_200_OK, status_msg)

            msg = f'Updating {k} failed'
            self.assertEqual(response_patch.data[k], data[k], msg)

    def test_delete_how_to(self):
        """
        Ensure client can delete Step
        """
        url = reverse('step-list')
        data = {'title' : 'Update a Step'}
        response_post = self.client.post(url, data, format = 'json')
        
        url_delete = reverse('step-detail', args = [response_post.data['uri_id']])
        response_delete = self.client.delete(url_delete, format = 'json')

        status_msg = 'HTTP status return code is not 204'
        self.assertEqual(response_delete.status_code, status.HTTP_204_NO_CONTENT, status_msg)

        url_get = reverse('step-detail', args = [response_post.data['uri_id']])
        response_get = self.client.get(url_get, data, format = 'json')
        status_msg = 'Step was not successfully deleted'
        self.assertEqual(response_get.status_code, status.HTTP_404_NOT_FOUND, status_msg)

    def test_forbidden_updates(self):
        """
        Ensure client can not change read only fields
        """
        url = reverse('step-list')
        data = {'title' : 'Forbidden update'}
        response_post = self.client.post(url, data, format = 'json')

        url = reverse('step-detail', args = [response_post.data['uri_id']])
        
        data = {
            'uri_id' : 'lolololo',
            'created' : 'lol',
        }

        for k, v in data.items():
            forbidden_data = {k : v}
            response_patch = self.client.patch(url, forbidden_data, format = 'json')

            msg = f'Forbidden update on {k} was not blocked'
            self.assertEqual(response_post.data[k], response_patch.data[k], msg)


class SuperStepTest(APITestCase):
    def test_link_unlink_substep_to_superstep(self):
        """
        Ensure client can link a Step to a Superstep, then delete it
        """
        # Create a Superstep
        url = reverse('step-list')
        data = {'title' : 'Superstep to link'}
        superstep = self.client.post(url, data, format = 'json')
        
        # Create a Substep
        url = reverse('step-list')
        data = {'title' : 'Substep to link'}
        substep = self.client.post(url, data, format = 'json')

        # Link Step to Superstep
        url = reverse('sub-step', args = [superstep.data['uri_id']])
        data = {'uri_id' : substep.data['uri_id']}
        self.client.post(url, data, format = 'json')

        # Check if Step was correctly linked
        url = reverse('step-detail', args = [superstep.data['uri_id']])
        response = self.client.get(url, format = 'json')

        msg = 'Step was not linked to Superstep correctly'
        self.assertEqual(response.data['substeps'][0]['uri_id'], substep.data['uri_id'], msg)

        # Unlink step
        url = reverse('super-detail', args = [superstep.data['uri_id'], substep.data['uri_id']])
        response = self.client.delete(url, format = 'json')

        # Check if Step was correctly unlinked
        url = reverse('step-detail', args = [superstep.data['uri_id']])
        response = self.client.get(url, format = 'json')

        msg = 'Step was not unlinked from Superstep correctly'
        self.assertFalse(len(response.data['substeps']), msg)

    def test_rearrange_substeps(self):
        """
        Ensure client can reorder substeps
        """
        # Create a Superstep
        url = reverse('step-list')
        data = {'title' : 'Superstep to link'}
        superstep = self.client.post(url, data, format = 'json')
        
        # Create Substeps
        url = reverse('step-list')
        data = {'title' : 'Substep1'}
        substep1 = self.client.post(url, data, format = 'json')
        data = {'title' : 'Substep2'}
        substep2 = self.client.post(url, data, format = 'json')

        # Link Step to Superstep
        url = reverse('sub-step', args = [superstep.data['uri_id']])
        data = {'uri_id' : substep1.data['uri_id']}
        self.client.post(url, data, format = 'json')
        data = {'uri_id' : substep2.data['uri_id']}
        self.client.post(url, data, format = 'json')

        # Check initial order
        url = reverse('step-detail', args = [superstep.data['uri_id']])
        response = self.client.get(url, format = 'json')
        steps = response.data['substeps']
        
        msg = 'Initial step position is not ok'
        self.assertEqual(steps[0]['uri_id'], substep1.data['uri_id'], msg)
        self.assertEqual(steps[1]['uri_id'], substep2.data['uri_id'], msg)

        # Reorder
        url = reverse('sub-step', args = [superstep.data['uri_id']])
        data = {'method' : 'order', 'old_index' : 0, 'new_index' : 1}
        response = self.client.patch(url, data, format = 'json')

        msg = 'Reorderung did not return 200'  
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg)  

        # Check new order
        url = reverse('step-detail', args = [superstep.data['uri_id']])
        response = self.client.get(url, format = 'json')
        steps = response.data['substeps']

        msg = 'Changed step position is not ok'
        self.assertEqual(steps[0]['uri_id'], substep2.data['uri_id'], msg)
        self.assertEqual(steps[1]['uri_id'], substep1.data['uri_id'], msg)