import re
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


class TestExplanationText():
    api_client = APIClient()

    @pytest.mark.django_db
    def test_create_text_explanation(self):
        """
        Ensure client can create a new Explanation text
        """
        url = reverse('explanation')
        data = {'type': 'text', 'title': 'Create an Explanation'}
        response = self.api_client.post(url, data, format='json')

        msg = 'HTTP status return code is not 201'
        assert response.status_code == status.HTTP_201_CREATED, msg

        msg = 'Created title is not correct'
        assert response.data['title'] == data['title'], msg

    @pytest.mark.django_db
    def test_retrieve_text_explanation_by_id(self):
        """
        Ensure client can retreive a Text Explanation by Uri ID
        """
        url = reverse('explanation')
        data = {'type': 'text', 'title': 'Create and Retrieve'}
        response_post = self.api_client.post(url, data, format='json')

        url = reverse('explanation-detail',
                      args=[response_post.data['api_id']])
        response_get = self.api_client.get(url, format='json')

        msg = 'Retreiving Text Explanation by Uri ID failed'
        assert response_get.status_code == status.HTTP_200_OK, msg

        msg = ('Retreiving Text Explanation by Uri ID did not return the '
               'correct explanation')
        assert response_get.data['title'] == data['title'], msg

    @pytest.mark.django_db
    def test_update_text_explanation(self):
        """
        Ensure client can update Text Explanation
        """
        url = reverse('explanation')
        data = {'type': 'text', 'title': 'Create and Retrieve'}
        response_post = self.api_client.post(url, data, format='json')

        url = reverse('explanation-detail',
                      args=[response_post.data['api_id']])
        status_msg = 'HTTP status return code is not 200'
        data = {
            'title': 'New Title',
            'content': 'New Content',
        }

        for k, v in data.items():
            change_data = {k: v}
            response_patch = self.api_client.patch(
                url, change_data, format='json')

            assert response_patch.status_code == status.HTTP_200_OK, status_msg

            msg = f'Updating {k} failed'
            assert response_patch.data[k] == data[k], msg

    @pytest.mark.django_db
    def test_delete_text_explanation(self):
        """
        Ensure client can delete Text Explanation
        """
        url = reverse('explanation')
        data = {'type': 'text', 'title': 'Create and Retrieve'}
        response_post = self.api_client.post(url, data, format='json')

        url_delete = reverse('explanation-detail',
                             args=[response_post.data['api_id']])
        response_delete = self.api_client.delete(url_delete, format='json')

        msg = 'HTTP status return code is not 204'
        assert response_delete.status_code == status.HTTP_204_NO_CONTENT, msg

        url_get = reverse('explanation-detail',
                          args=[response_post.data['api_id']])
        response_get = self.api_client.get(url_get, data, format='json')
        msg = 'Text Explanation was not successfully deleted'
        assert response_get.status_code == status.HTTP_404_NOT_FOUND, msg

    @pytest.mark.django_db
    def test_forbidden_updates(self):
        """
        Ensure client can not change read only fields
        """
        url = reverse('explanation')
        data = {'type': 'text', 'title': 'Create and Retrieve'}
        response_post = self.api_client.post(url, data, format='json')

        url = reverse('explanation-detail',
                      args=[response_post.data['api_id']])

        data = {
            'api_id': 'lolololo',
            'created': 'lol',
        }

        for k, v in data.items():
            forbidden_data = {k: v}
            response_patch = self.api_client.patch(
                url, forbidden_data, format='json')

            msg = f'Forbidden update on {k} was not blocked'
            assert response_post.data[k] == response_patch.data[k], msg


class TestExplanationCode():
    api_client = APIClient()

    @pytest.mark.django_db
    def test_create_text_explanation(self):
        """
        Ensure client can create a new Explanation text
        """
        url = reverse('explanation')
        data = {'type': 'code', 'title': 'Create an Explanation'}
        response = self.api_client.post(url, data, format='json')

        msg = 'HTTP status return code is not 201'
        assert response.status_code == status.HTTP_201_CREATED, msg

        msg = 'Created title is not correct'
        assert response.data['title'] == data['title'], msg

    @pytest.mark.django_db
    def test_retrieve_code_explanation_by_id(self):
        """
        Ensure client can retreive a Code Explanation by Uri ID
        """
        url = reverse('explanation')
        data = {'type': 'code', 'title': 'Create and Retrieve'}
        response_post = self.api_client.post(url, data, format='json')

        url = reverse('explanation-detail',
                      args=[response_post.data['api_id']])
        response_get = self.api_client.get(url, format='json')

        msg = 'Retreiving Code Explanation by Uri ID failed'
        assert response_get.status_code == status.HTTP_200_OK, msg

        msg = ('Retreiving Code Explanation by Uri ID did not return the '
               'correct explanation')
        assert response_get.data['title'] == data['title'], msg

    @pytest.mark.django_db
    def test_update_code_explanation(self):
        """
        Ensure client can update Code Explanation
        """
        url = reverse('explanation')
        data = {'type': 'code', 'title': 'Create and Retrieve'}
        response_post = self.api_client.post(url, data, format='json')

        url = reverse('explanation-detail',
                      args=[response_post.data['api_id']])
        status_msg = 'HTTP status return code is not 200'
        data = {
            'title': 'New Title',
            'content': 'New Content',
        }

        for k, v in data.items():
            change_data = {k: v}
            response_patch = self.api_client.patch(
                url, change_data, format='json')

            assert response_patch.status_code == status.HTTP_200_OK, status_msg

            msg = f'Updating {k} failed'
            assert response_patch.data[k] == data[k], msg

    @pytest.mark.django_db
    def test_delete_code_explanation(self):
        """
        Ensure client can delete Code Explanation
        """
        url = reverse('explanation')
        data = {'type': 'code', 'title': 'Create and Retrieve'}
        response_post = self.api_client.post(url, data, format='json')

        url_delete = reverse('explanation-detail',
                             args=[response_post.data['api_id']])
        response_delete = self.api_client.delete(url_delete, format='json')

        msg = 'HTTP status return code is not 204'
        assert response_delete.status_code == status.HTTP_204_NO_CONTENT, msg

        url_get = reverse('explanation-detail',
                          args=[response_post.data['api_id']])
        response_get = self.api_client.get(url_get, data, format='json')
        msg = 'Code Explanation was not successfully deleted'
        assert response_get.status_code == status.HTTP_404_NOT_FOUND, msg

    @pytest.mark.django_db
    def test_forbidden_updates(self):
        """
        Ensure client can not change read only fields
        """
        url = reverse('explanation')
        data = {'type': 'code', 'title': 'Create and Retrieve'}
        response_post = self.api_client.post(url, data, format='json')

        url = reverse('explanation-detail',
                      args=[response_post.data['api_id']])

        data = {
            'api_id': 'lolololo',
            'created': 'lol',
        }

        for k, v in data.items():
            forbidden_data = {k: v}
            response_patch = self.api_client.patch(
                url, forbidden_data, format='json')

            msg = f'Forbidden update on {k} was not blocked'
            assert response_post.data[k] == response_patch.data[k], msg
