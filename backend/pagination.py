from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.response import Response


class CustomPagination(LimitOffsetPagination):
    default_limit = 10

    def get_paginated_response(self, data):
        return Response(data)
