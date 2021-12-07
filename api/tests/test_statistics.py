import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


class TestStatistics():
    api_client = APIClient()

    @pytest.mark.django_db
    def test_get_statistics(self):
        """
        Ensure client can retreive statistics
        """
        url = reverse('statistics')
        response = self.api_client.get(url, format='json')

        msg = 'HTTP status return code is not 200'
        assert response.status_code == status.HTTP_200_OK, msg
