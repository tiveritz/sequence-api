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
        response = self.client.post(url, data, format = 'json')
        
        url = reverse('how-to-detail', args = [response.data['uri_id']])
        data = {'title' : 'New Title', 'description' : 'New Description'}
        response = self.client.patch(url, data, format = 'json')

        msg = 'HTTP status return code is not 200'
        self.assertEqual(response.status_code,status.HTTP_200_OK, msg)

        msg = 'Change title failed'  
        self.assertEqual(response.data['title'], data['title'], msg)

