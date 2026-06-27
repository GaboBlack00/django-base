from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination

from apps.core.response import api_response


class UnifiedPageNumberPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        return api_response(
            success=True,
            data=OrderedDict(
                [
                    ("count", self.page.paginator.count),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("results", data),
                ]
            ),
        )
