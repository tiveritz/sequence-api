from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

class Statistics(APITestCase):
    def test_get_statistics(self):
        """
        Ensure client can retreive statistics
        """
        url = reverse('statistics')
        response = self.client.get(url, format='json')

        msg = 'HTTP status return code is not 200'
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg)
