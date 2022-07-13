from math import ceil

from django.conf import settings
from django.core.paginator import EmptyPage
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class ListPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        page_size = settings.REST_FRAMEWORK['PAGE_SIZE']
        return Response({
            'next_url': self.get_next_link(),
            'previous_url': self.get_previous_link(),
            'next': self.next_page_number(),
            'previous': self.previous_page_number(),
            'current': self.page.number,
            'pages': ceil(self.page.paginator.count / page_size),
            'count': self.page.paginator.count,
            'results': data
        })

    def previous_page_number(self):
        try:
            return self.page.previous_page_number()
        except EmptyPage:
            return None

    def next_page_number(self):
        try:
            return self.page.next_page_number()
        except EmptyPage:
            return None
