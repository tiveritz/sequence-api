from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from math import ceil
from django.conf import settings


class ListPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        page_size = settings.REST_FRAMEWORK['PAGE_SIZE']
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'pages': ceil(self.page.paginator.count / page_size),
            'results': data
        })
