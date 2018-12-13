# from rest_framework.pagination import LimitOffsetPagination
from rest_framework import pagination
from rest_framework.response import Response


class LimitOffsetPagination(pagination.LimitOffsetPagination):
    def get_paginated_response(self, data):
        return Response({
            "articlesCount": self.count,
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            "results": data
        })
