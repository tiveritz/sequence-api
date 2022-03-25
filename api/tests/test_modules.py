import re
import pytest
from django.urls import reverse
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient


class TestModules():
    api_client = APIClient()

    @pytest.mark.django_db
    def test_add_text_explanation_module_to_step(self, step):
        """
        Ensure client can add a text explanation to step
        """
        # Create Explanation
        url = reverse('explanation')
        data = {'type': 'text', 'title': 'Create and add to step'}
        response_explanation = self.api_client.post(url, data, format='json')

        # Add Explanation to Step
        url = reverse('step-module', args=[step.api_id])
        data = {
            'api_id': response_explanation.data['api_id'],
            'type': 'explanation',
        }
        response_module = self.api_client.post(url, data, format='json')

        msg = 'HTTP status return code is not 201'
        assert response_module.status_code == status.HTTP_201_CREATED, msg

        # Check if Explanation was correctly added
        url = reverse('step-module', args=[step.api_id])
        response_get = self.api_client.get(url, format='json')

        msg = 'Could not retrieve step module by api_id'
        response_api_id = response_get.data[0]['api_id']
        data_api_id = response_explanation.data['api_id']
        assert response_api_id == data_api_id, msg

    @pytest.mark.django_db
    def test_add_code_explanation_module_to_step(self, step):
        """
        Ensure client can add a code epxlanation to a step
        """
        # Create Explanation
        url = reverse('explanation')
        data = {'type': 'code', 'title': 'Create and add to step'}
        response_explanation = self.api_client.post(url, data, format='json')

        # Add Explanation to Step
        url = reverse('step-module', args=[step.api_id])
        data = {
            'api_id': response_explanation.data['api_id'],
            'type': 'explanation',
        }
        response_module = self.api_client.post(url, data, format='json')

        msg = 'HTTP status return code is not 201'
        assert response_module.status_code == status.HTTP_201_CREATED, msg

        # Check if Explanation was correctly added
        url = reverse('step-module', args=[step.api_id])
        response_get = self.api_client.get(url, format='json')

        msg = 'Could not retrieve step module by api_id'
        response_api_id = response_get.data[0]['api_id']
        data_api_id = response_explanation.data['api_id']
        assert response_api_id == data_api_id, msg

    @pytest.mark.django_db
    def test_rearrange_modules(self, step):
        """
        Ensure client can reorder modules
        """
        # Create Modules
        url = reverse('explanation')
        data = {'type': 'text', 'title': 'Create and add to step'}
        response_text_module = self.api_client.post(url, data, format='json')
        data = {'type': 'code', 'title': 'Create and add to step'}
        response_code_module = self.api_client.post(url, data, format='json')

        # Add Modules to Step
        url = reverse('step-module', args=[step.api_id])
        data = {
            'api_id': response_text_module.data['api_id'],
            'type': 'explanation',
        }
        self.api_client.post(url, data, format='json')
        data = {
            'api_id': response_code_module.data['api_id'],
            'type': 'explanation',
        }
        self.api_client.post(url, data, format='json')

        # Check initial order
        url = reverse('step-module', args=[step.api_id])
        modules = self.api_client.get(url, format='json').data

        msg = 'Initial module position is not ok'
        assert modules[0]['api_id'] == response_text_module.data['api_id'], msg
        assert modules[1]['api_id'] == response_code_module.data['api_id'], msg

        # Reorder
        url = reverse('step-module', args=[step.api_id])
        data = {'method': 'order', 'old_index': 0, 'new_index': 1}
        response = self.api_client.patch(url, data, format='json')

        msg = 'Reorderung modules did not return 200'
        assert response.status_code == status.HTTP_200_OK, msg

        # Check new order
        url = reverse('step-module', args=[step.api_id])
        modules = self.api_client.get(url, format='json').data

        msg = 'Changed module position is not ok'
        assert modules[0]['api_id'] == response_code_module.data['api_id'], msg
        assert modules[1]['api_id'] == response_text_module.data['api_id'], msg

    @pytest.mark.django_db
    def test_delete_module(self, step):
        """
        Ensure client can delete modules
        """
        # Create Explanation
        url = reverse('explanation')
        data = {'type': 'text', 'title': 'Create and add to step'}
        response_explanation = self.api_client.post(url, data, format='json')

        # Add Explanation to Step
        url = reverse('step-module', args=[step.api_id])
        data = {
            'api_id': response_explanation.data['api_id'],
            'type': 'explanation',
        }
        self.api_client.post(url, data, format='json')

        # Check if Explanation was correctly linked
        url = reverse('step-module', args=[step.api_id])
        response_get = self.api_client.get(url, format='json')

        msg = 'Could not retrieve step module by api_id'
        response_api_id = response_get.data[0]['api_id']
        data_api_id = response_explanation.data['api_id']
        assert response_api_id == data_api_id, msg

        # Delete
        url = reverse('step-module', args=[step.api_id])
        data = {'method': 'delete',
                'api_id': response_explanation.data['api_id']}
        response = self.api_client.patch(url, data, format='json')

        msg = 'Deleting Substep did not return 200'
        assert response.status_code == status.HTTP_200_OK, msg

        # Check if successfully deleted
        url = reverse('step-module', args=[step.api_id])
        modules = self.api_client.get(url, format='json').data

        msg = 'Deleting Substep was not successfull'
        assert len(modules) == 0, msg


class TestImage():
    api_client = APIClient()

    @pytest.mark.django_db
    def test_add_delete_png_image(self):
        """
        Ensure client can add a image
        """
        url = reverse('images')
        image = SimpleUploadedFile(
            name='test_image.png', content=b'', content_type='image/png')
        data = {
            "image": image
        }
        response_post = self.api_client.post(url, data)

        msg = 'HTTP status return code is not 201'
        assert response_post.status_code == status.HTTP_201_CREATED, msg

        msg = 'Created title is not correct'
        assert response_post.data['title'] == 'test_image.png', msg

        msg = 'Created image name is not correct'
        image_name = '/' + response_post.data['api_id'] + '.png'
        is_correct = image_name in response_post.data['image']
        assert is_correct, msg

        url = reverse('image-detail', args=[response_post.data['api_id']])
        msg = 'Image deletion does not work'
        response_delete = self.api_client.delete(url)
        assert response_delete.status_code == status.HTTP_204_NO_CONTENT, msg

        url = reverse('image-detail', args=[response_post.data['api_id']])
        response_get = self.api_client.get(url)
        assert response_get.status_code == status.HTTP_404_NOT_FOUND, msg

    @pytest.mark.django_db
    def test_add_jpg_image(self):
        """
        Ensure client can add a image
        """
        url = reverse('images')
        image = SimpleUploadedFile(
            name='test_image.jpg', content=b'', content_type='image/jpg')
        data = {
            "image": image
        }
        response_post = self.api_client.post(url, data)

        msg = 'HTTP status return code is not 201'
        assert response_post.status_code == status.HTTP_201_CREATED, msg

        msg = 'Created title is not correct'
        assert response_post.data['title'] == 'test_image.jpg', msg

        msg = 'Created image name is not correct'
        image_name = '/' + response_post.data['api_id'] + '.jpg'
        is_correct = image_name in response_post.data['image']
        assert is_correct, msg

        url = reverse('image-detail', args=[response_post.data['api_id']])
        msg = 'Image deletion does not work'
        response_delete = self.api_client.delete(url)
        assert response_delete.status_code == status.HTTP_204_NO_CONTENT, msg

        url = reverse('image-detail', args=[response_post.data['api_id']])
        response_get = self.api_client.get(url)
        assert response_get.status_code == status.HTTP_404_NOT_FOUND, msg

    @pytest.mark.django_db
    def test_add_image_module_to_step(self, step):
        """
        Ensure client can add image module to step
        """
        # Create Image
        url = reverse('images')
        image = SimpleUploadedFile(
            name='test_image.jpg', content=b'', content_type='image/jpg')
        data = {
            "image": image
        }
        response_image = self.api_client.post(url, data)

        # Add Image to Step
        url = reverse('step-module', args=[step.api_id])
        data = {
            'api_id': response_image.data['api_id'],
            'type': 'image',
        }
        response_module = self.api_client.post(url, data, format='json')

        msg = 'HTTP status return code is not 201'
        assert response_module.status_code == status.HTTP_201_CREATED, msg

        # Delete Image
        url = reverse('image-detail', args=[response_image.data['api_id']])
        self.api_client.delete(url)
