import re
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile


class ModulesTest(APITestCase):
    def test_add_text_explanation_module_to_step(self):
        """
        Ensure client can add a text explanation to step
        """
        # Create Step
        url = reverse('step-list')
        data = {'title' : 'new'}
        response_step = self.client.post(url, data, format='json')

        # Create Explanation
        url = reverse('explanation')
        data = {'type': 'text', 'title' : 'Create and add to step'}
        response_explanation = self.client.post(url, data, format='json')

        # Add Explanation to Step
        url = reverse('step-module', args=[response_step.data['uri_id']])
        data = {
            'uri_id': response_explanation.data['uri_id'],
            'type': 'explanation',
            }
        response_module = self.client.post(url, data, format='json')

        msg = 'HTTP status return code is not 201'
        self.assertEqual(response_module.status_code, status.HTTP_201_CREATED, msg)

        # Check if Explanation was correctly added
        url = reverse('step-module', args=[response_step.data['uri_id']])
        response_get = self.client.get(url, format='json')

        msg = 'Could not retrieve step module by uri_id' 
        self.assertEqual(response_get.data[0]['uri_id'], response_explanation.data['uri_id'], msg)   
    
    def test_add_code_explanation_module_to_step(self):
        """
        Ensure client can add a code epxlanation to a step
        """
        # Create Step
        url = reverse('step-list')
        data = {'title' : 'new'}
        response_step = self.client.post(url, data, format='json')

        # Create Explanation
        url = reverse('explanation')
        data = {'type': 'code', 'title' : 'Create and add to step'}
        response_explanation = self.client.post(url, data, format='json')

        # Add Explanation to Step
        url = reverse('step-module', args=[response_step.data['uri_id']])
        data = {
            'uri_id': response_explanation.data['uri_id'],
            'type': 'explanation',
            }
        response_module = self.client.post(url, data, format='json')

        msg = 'HTTP status return code is not 201'
        self.assertEqual(response_module.status_code, status.HTTP_201_CREATED, msg)

        # Check if Explanation was correctly added
        url = reverse('step-module', args=[response_step.data['uri_id']])
        response_get = self.client.get(url, format='json')

        msg = 'Could not retrieve step module by uri_id' 
        self.assertEqual(response_get.data[0]['uri_id'], response_explanation.data['uri_id'], msg)    

    def test_rearrange_modules(self):
        """
        Ensure client can reorder modules
        """
        # Create Step
        url = reverse('step-list')
        data = {'title' : 'new'}
        response_step = self.client.post(url, data, format='json')
        
        # Create Modules
        url = reverse('explanation')
        data = {'type': 'text', 'title' : 'Create and add to step'}
        response_text_module = self.client.post(url, data, format='json')
        data = {'type': 'code', 'title' : 'Create and add to step'}
        response_code_module = self.client.post(url, data, format='json')

        # Add Modules to Step
        url = reverse('step-module', args=[response_step.data['uri_id']])
        data = {
            'uri_id': response_text_module.data['uri_id'],
            'type': 'explanation',
            }
        self.client.post(url, data, format='json')
        data = {
            'uri_id': response_code_module.data['uri_id'],
            'type': 'explanation',
            }
        self.client.post(url, data, format='json')

        # Check initial order
        url = reverse('step-module', args=[response_step.data['uri_id']])
        modules = self.client.get(url, format='json').data

        msg = 'Initial module position is not ok'
        self.assertEqual(modules[0]['uri_id'], response_text_module.data['uri_id'], msg)
        self.assertEqual(modules[1]['uri_id'], response_code_module.data['uri_id'], msg)

        # Reorder
        url = reverse('step-module', args=[response_step.data['uri_id']])
        data = {'method' : 'order', 'old_index' : 0, 'new_index' : 1}
        response = self.client.patch(url, data, format='json')

        msg = 'Reorderung modules did not return 200'  
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg)  

        # Check new order
        url = reverse('step-module', args=[response_step.data['uri_id']])
        modules = self.client.get(url, format='json').data

        msg = 'Changed module position is not ok'
        self.assertEqual(modules[0]['uri_id'], response_code_module.data['uri_id'], msg)
        self.assertEqual(modules[1]['uri_id'], response_text_module.data['uri_id'], msg)

    def test_delete_module(self):
        """
        Ensure client can delete modules
        """
        # Create Step
        url = reverse('step-list')
        data = {'title' : 'new'}
        response_step = self.client.post(url, data, format='json')

        # Create Explanation
        url = reverse('explanation')
        data = {'type': 'text', 'title' : 'Create and add to step'}
        response_explanation = self.client.post(url, data, format='json')

        # Add Explanation to Step
        url = reverse('step-module', args=[response_step.data['uri_id']])
        data = {
            'uri_id': response_explanation.data['uri_id'],
            'type': 'explanation',
            }
        response_module = self.client.post(url, data, format='json')

        # Check if Explanation was correctly linked
        url = reverse('step-module', args=[response_step.data['uri_id']])
        response_get = self.client.get(url, format='json')

        msg = 'Could not retrieve step module by uri_id' 
        self.assertEqual(response_get.data[0]['uri_id'], response_explanation.data['uri_id'], msg)  

        # Delete
        url = reverse('step-module', args=[response_step.data['uri_id']])
        data = {'method' : 'delete', 'uri_id' : response_explanation.data['uri_id']}
        response = self.client.patch(url, data, format='json')

        msg = 'Deleting Substep did not return 200'  
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg)  

        # Check if successfully deleted
        url = reverse('step-module', args=[response_step.data['uri_id']])
        modules = self.client.get(url, format='json').data

        msg = 'Deleting Substep was not successfull'  
        self.assertEqual(len(modules), 0, msg)

class ImageTest(APITestCase):
    def test_add_png_image(self):
        """
        Ensure client can add a image
        """
        url = reverse('images')
        image = SimpleUploadedFile(name='test_image.png', content=b'', content_type='image/png')
        data = {
            "image": image
        }
        response = self.client.post(url, data)

        msg = 'HTTP status return code is not 201'
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg)

        msg = 'Created title is not correct'
        self.assertEqual(response.data['title'], 'test_image.png', msg)

        msg = 'Created Uri ID is not correct'
        # Matches any word with lower letters, numbers with a exact length of
        # 8 characters
        pattern = re.compile(r'^[a-z0-9]{8}$')
        is_match = re.match(pattern, str(response.data['uri_id'])) or False
        self.assertTrue(is_match, msg)

        msg = 'Created image name is not correct'
        image_name = '/' + response.data['uri_id'] + '.png'
        is_correct = image_name in response.data['image']
        self.assertTrue(is_correct, msg)

    def test_add_jpg_image(self):
        """
        Ensure client can add a image
        """
        url = reverse('images')
        image = SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpg')
        data = {
            "image": image
        }
        response = self.client.post(url, data)

        msg = 'HTTP status return code is not 201'
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg)

        msg = 'Created title is not correct'
        self.assertEqual(response.data['title'], 'test_image.jpg', msg)

        msg = 'Created Uri ID is not correct'
        # Matches any word with lower letters, numbers with a exact length of
        # 8 characters
        pattern = re.compile(r'^[a-z0-9]{8}$')
        is_match = re.match(pattern, str(response.data['uri_id'])) or False
        self.assertTrue(is_match, msg)

        msg = 'Created image name is not correct'
        image_name = '/' + response.data['uri_id'] + '.jpg'
        is_correct = image_name in response.data['image']
        self.assertTrue(is_correct, msg)

    def test_add_image_module_to_step(self):
        """
        Ensure client can add image module to step
        """

        # Create Step
        url = reverse('step-list')
        data = {'title' : 'new'}
        response_step = self.client.post(url, data, format='json')

        # Create Image
        url = reverse('images')
        image = SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpg')
        data = {
            "image": image
        }
        response_image = self.client.post(url, data)

        # Add Image to Step
        url = reverse('step-module', args=[response_step.data['uri_id']])
        data = {
            'uri_id': response_image.data['uri_id'],
            'type': 'image',
            }
        response_module = self.client.post(url, data, format='json')

        msg = 'HTTP status return code is not 201'
        self.assertEqual(response_module.status_code, status.HTTP_201_CREATED, msg)     