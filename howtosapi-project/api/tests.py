import re
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class HowToTests(APITestCase):
    def test_create_how_to(self):
        """
        Ensure client can create a new How To
        """
        url = reverse('how-to-list')
        data = {'title' : 'How to Create a How To'}
        response = self.client.post(url, data, format = 'json')

        msg = 'HTTP status return code is not 201'
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg)

        msg = 'Created data is not correct'  
        self.assertEqual(response.data['title'], data['title'], msg)

        msg = 'Uri ID was not created correctly'
        # Matches any word with lower letters, numbers with a exact length of
        # 8 characters
        #pattern = re.compile(r'^[a-z0-9]{8}$')
        pattern = re.compile(r'^[a-z0-9]{8}$')
        is_match = re.match(pattern, str(response.data['uri_id'])) or False
        self.assertTrue(is_match, msg)

    def test_retrieve_how_to_by_id(self):
        """
        Ensure client can retreive a How To by Uri ID
        """
        url = reverse('how-to-list')
        data = {'title' : 'new'}
        response_post = self.client.post(url, data, format = 'json')

        url = reverse('how-to-detail', args = [response_post.data['uri_id']])
        response_get = self.client.get(url, format = 'json')
        
        msg = 'Retreiving How To by Uri ID failed'  
        self.assertEqual(response_post.data['title'], data['title'], msg)
    

    def test_update_how_to(self):
        """
        Ensure client can update How To
        """
        url = reverse('how-to-list')
        data = {'title' : 'Update a How To'}
        response_post = self.client.post(url, data, format = 'json')
        
        url = reverse('how-to-detail', args = [response_post.data['uri_id']])
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
        
    def test_forbidden_updates(self):
        """
        Ensure client can not change read only fields
        """
        url = reverse('how-to-list')
        data = {'title' : 'Forbidden update'}
        response_post = self.client.post(url, data, format = 'json')

        url = reverse('how-to-detail', args = [response_post.data['uri_id']])
        
        data = {
            'uri_id' : 'lolololo',
            'created' : 'lol',
        }

        for k, v in data.items():
            forbidden_data = {k : v}
            response_patch = self.client.patch(url, forbidden_data, format = 'json')

            msg = f'Forbidden update on {k} was not blocked'
            self.assertEqual(response_post.data[k], response_patch.data[k], msg)


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
        #pattern = re.compile(r'^[a-z0-9]{8}$')
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
        
        msg = 'Retreiving Step by Uri ID failed'  
        self.assertEqual(response_post.data['title'], data['title'], msg)

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
    
class HowToStepTest(APITestCase):
    def test_link_unlink_step_to_how_to(self):
        """
        Ensure client can link a Step to a How to, then delete it
        """
        # Create a How To
        url = reverse('how-to-list')
        data = {'title' : 'Linkable How To'}
        how_to = self.client.post(url, data, format = 'json')
        
        # Create a Step
        url = reverse('step-list')
        data = {'title' : 'Step to link'}
        step = self.client.post(url, data, format = 'json')

        # Link Step to How To
        url = reverse('how-to-step', args = [how_to.data['uri_id']])
        data = {'uri_id' : step.data['uri_id']}
        self.client.post(url, data, format = 'json')

        # Check if Step was correctly linked
        url = reverse('how-to-detail', args = [how_to.data['uri_id']])
        response = self.client.get(url, format = 'json')

        msg = 'Step was not linked to How To correctly'
        self.assertEqual(response.data['steps'][0]['uri_id'], step.data['uri_id'], msg)

        # Unlink step
        url = reverse('how-to-step-detail', args = [how_to.data['uri_id'], step.data['uri_id']])
        response = self.client.delete(url, format = 'json')

        # Check if Step was correctly unlinked
        url = reverse('how-to-detail', args = [how_to.data['uri_id']])
        response = self.client.get(url, format = 'json')

        msg = 'Step was not unlinked from How To correctly'
        self.assertFalse(len(response.data['steps']), msg)

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

class DataIntegrityTest(APITestCase):
    def test_forbidden_how_to_step_duplicate(self):
        """
        Ensure client can not add a Substep to a How To more than once
        """
        # Create a How To
        url = reverse('how-to-list')
        data = {'title' : 'Linkable How To'}
        how_to = self.client.post(url, data, format = 'json')

        # Create a Substep
        url = reverse('step-list')
        data = {'title' : 'Super'}
        step = self.client.post(url, data, format = 'json')

        # Link Step to How To
        url = reverse('how-to-step', args = [how_to.data['uri_id']])
        data = {'uri_id' : step.data['uri_id']}
        self.client.post(url, data, format = 'json')

        # Try to link the step a second time
        url = reverse('how-to-step', args = [how_to.data['uri_id']])
        data = {'uri_id' : step.data['uri_id']}
        response = self.client.post(url, data, format = 'json')

        msg = 'Adding duplicate Substeps in a How To did not return correct status code'
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, msg)

    def test_forbidden_step_duplicate(self):
        """
        Ensure client can not add a Substep to a Superstep more than once
        """
        # Create a Superstep
        url = reverse('step-list')
        data = {'title' : 'Super'}
        superstep = self.client.post(url, data, format = 'json')

        # Create a Substep
        url = reverse('step-list')
        data = {'title' : 'Super'}
        substep = self.client.post(url, data, format = 'json')

        # Link Step to Superstep
        url = reverse('sub-step', args = [superstep.data['uri_id']])
        data = {'uri_id' : substep.data['uri_id']}
        self.client.post(url, data, format = 'json')

        # Try to link the step a second time
        url = reverse('sub-step', args = [superstep.data['uri_id']])
        data = {'uri_id' : substep.data['uri_id']}
        response = self.client.post(url, data, format = 'json')

        msg = 'Adding duplicate Substeps in a Superstep did not return correct status code'
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, msg)

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
            'a' : None,
            'b' : None,
            'c' : None,
            'd' : None,
            'e' : None,
            'f' : None,
        }

        url = reverse('step-list')
        for stepname in steps:
            data = {'title' : stepname}
            steps[stepname] = self.client.post(url, data, format = 'json')

        # Link Steps
        links = [
            (steps['b'], steps['a']),
            (steps['c'], steps['b']),
            (steps['b'], steps['d']),
            (steps['f'], steps['e']),
            (steps['b'], steps['f']),
        ]

        for link in links:
            url = reverse('sub-step', args = [link[0].data['uri_id']])
            data = {'uri_id' : link[1].data['uri_id']}
            self.client.post(url, data, format = 'json')

        # Try to link d to a -> conflict b (already linked to a)
        url = reverse('sub-step', args = [steps['c'].data['uri_id']])
        data = {'uri_id' : steps['e'].data['uri_id']}
        response = self.client.post(url, data, format = 'json')
        
        msg = 'Adding forbidden circular reference was not blocked'
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, msg)
