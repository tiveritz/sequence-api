import pytest
from rest_framework.test import APIClient


class TestSequence():
    api_client = APIClient()

    @pytest.mark.django_db
    def test_publish(self):
        pass
