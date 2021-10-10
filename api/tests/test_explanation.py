import re
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class ExplanationTextTests(APITestCase):
    def test_create_text_explanation(self):
        """
        Ensure client can create a new Explanation text
        """
        url = reverse('explanation')
        data = {'type': 'text', 'title' : 'How to Create an Explanation'}
        response = self.client.post(url, data, format='json')

        msg = 'HTTP status return code is not 201'
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg)

        msg = 'Created title is not correct'
        self.assertEqual(response.data['title'], data['title'], msg)

        msg = 'Created Uri ID is not correct'
        # Matches any word with lower letters, numbers with a exact length of
        # 8 characters
        pattern = re.compile(r'^[a-z0-9]{8}$')
        is_match = re.match(pattern, str(response.data['uri_id'])) or False
        self.assertTrue(is_match, msg)  

    def test_retrieve_text_explanation_by_id(self):
        """
        Ensure client can retreive a Text Explanation by Uri ID
        """
        url = reverse('explanation')
        data = {'type': 'text', 'title' : 'Create and Retrieve'}
        response_post = self.client.post(url, data, format='json')

        url = reverse('explanation-detail', args=[response_post.data['uri_id']])
        response_get = self.client.get(url, format='json')

        msg = 'Retreiving Text Explanation by Uri ID failed'  
        self.assertEqual(response_get.status_code, status.HTTP_200_OK, msg)      
        
        msg = 'Retreiving Text Explanation by Uri ID did not return the correct explanation'  
        self.assertEqual(response_get.data['title'], data['title'], msg)

    def test_update_text_explanation(self):
        """
        Ensure client can update Text Explanation
        """
        url = reverse('explanation')
        data = {'type': 'text', 'title' : 'Create and Retrieve'}
        response_post = self.client.post(url, data, format='json')
        
        url = reverse('explanation-detail', args=[response_post.data['uri_id']])
        status_msg = 'HTTP status return code is not 200'
        data = {
            'title' : 'New Title',
            'content' : 'New Content',
        }

        for k, v in data.items():
            change_data = {k : v}
            response_patch = self.client.patch(url, change_data, format='json')

            self.assertEqual(response_patch.status_code, status.HTTP_200_OK, status_msg)

            msg = f'Updating {k} failed'
            self.assertEqual(response_patch.data[k], data[k], msg)

    def test_delete_text_explanation(self):
        """
        Ensure client can delete Text Explanation
        """
        url = reverse('explanation')
        data = {'type': 'text', 'title' : 'Create and Retrieve'}
        response_post = self.client.post(url, data, format='json')
        
        url_delete = reverse('explanation-detail', args=[response_post.data['uri_id']])
        response_delete = self.client.delete(url_delete, format='json')

        status_msg = 'HTTP status return code is not 204'
        self.assertEqual(response_delete.status_code, status.HTTP_204_NO_CONTENT, status_msg)

        url_get = reverse('explanation-detail', args=[response_post.data['uri_id']])
        response_get = self.client.get(url_get, data, format='json')
        status_msg = 'Text Explanation was not successfully deleted'
        self.assertEqual(response_get.status_code, status.HTTP_404_NOT_FOUND, status_msg)

    def test_forbidden_updates(self):
        """
        Ensure client can not change read only fields
        """
        url = reverse('explanation')
        data = {'type': 'text', 'title' : 'Create and Retrieve'}
        response_post = self.client.post(url, data, format='json')

        url = reverse('explanation-detail', args=[response_post.data['uri_id']])
        
        data = {
            'uri_id' : 'lolololo',
            'created' : 'lol',
        }

        for k, v in data.items():
            forbidden_data = {k : v}
            response_patch = self.client.patch(url, forbidden_data, format='json')

            msg = f'Forbidden update on {k} was not blocked'
            self.assertEqual(response_post.data[k], response_patch.data[k], msg)

class ExplanationCodeTests(APITestCase):
    def test_create_text_explanation(self):
        """
        Ensure client can create a new Explanation text
        """
        url = reverse('explanation')
        data = {'type': 'code', 'title' : 'How to Create an Explanation'}
        response = self.client.post(url, data, format='json')

        msg = 'HTTP status return code is not 201'
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg)

        msg = 'Created title is not correct'
        self.assertEqual(response.data['title'], data['title'], msg)

        msg = 'Created Uri ID is not correct'
        # Matches any word with lower letters, numbers with a exact length of
        # 8 characters
        pattern = re.compile(r'^[a-z0-9]{8}$')
        is_match = re.match(pattern, str(response.data['uri_id'])) or False
        self.assertTrue(is_match, msg)  

    def test_retrieve_code_explanation_by_id(self):
        """
        Ensure client can retreive a Code Explanation by Uri ID
        """
        url = reverse('explanation')
        data = {'type': 'code', 'title' : 'Create and Retrieve'}
        response_post = self.client.post(url, data, format='json')

        url = reverse('explanation-detail', args=[response_post.data['uri_id']])
        response_get = self.client.get(url, format='json')

        msg = 'Retreiving Code Explanation by Uri ID failed'  
        self.assertEqual(response_get.status_code, status.HTTP_200_OK, msg)      
        
        msg = 'Retreiving Code Explanation by Uri ID did not return the correct explanation'  
        self.assertEqual(response_get.data['title'], data['title'], msg)

    def test_update_code_explanation(self):
        """
        Ensure client can update Code Explanation
        """
        url = reverse('explanation')
        data = {'type': 'code', 'title' : 'Create and Retrieve'}
        response_post = self.client.post(url, data, format='json')
        
        url = reverse('explanation-detail', args=[response_post.data['uri_id']])
        status_msg = 'HTTP status return code is not 200'
        data = {
            'title' : 'New Title',
            'content' : 'New Content',
        }

        for k, v in data.items():
            change_data = {k : v}
            response_patch = self.client.patch(url, change_data, format='json')

            self.assertEqual(response_patch.status_code, status.HTTP_200_OK, status_msg)

            msg = f'Updating {k} failed'
            self.assertEqual(response_patch.data[k], data[k], msg)

    def test_delete_code_explanation(self):
        """
        Ensure client can delete Code Explanation
        """
        url = reverse('explanation')
        data = {'type': 'code', 'title' : 'Create and Retrieve'}
        response_post = self.client.post(url, data, format='json')
        
        url_delete = reverse('explanation-detail', args=[response_post.data['uri_id']])
        response_delete = self.client.delete(url_delete, format='json')

        status_msg = 'HTTP status return code is not 204'
        self.assertEqual(response_delete.status_code, status.HTTP_204_NO_CONTENT, status_msg)

        url_get = reverse('explanation-detail', args=[response_post.data['uri_id']])
        response_get = self.client.get(url_get, data, format='json')
        status_msg = 'Code Explanation was not successfully deleted'
        self.assertEqual(response_get.status_code, status.HTTP_404_NOT_FOUND, status_msg)

    def test_forbidden_updates(self):
        """
        Ensure client can not change read only fields
        """
        url = reverse('explanation')
        data = {'type': 'code', 'title' : 'Create and Retrieve'}
        response_post = self.client.post(url, data, format='json')

        url = reverse('explanation-detail', args=[response_post.data['uri_id']])
        
        data = {
            'uri_id' : 'lolololo',
            'created' : 'lol',
        }

        for k, v in data.items():
            forbidden_data = {k : v}
            response_patch = self.client.patch(url, forbidden_data, format='json')

            msg = f'Forbidden update on {k} was not blocked'
            self.assertEqual(response_post.data[k], response_patch.data[k], msg)