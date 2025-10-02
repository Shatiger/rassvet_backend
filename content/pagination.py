from collections import OrderedDict

from rest_framework.exceptions import ValidationError
from rest_framework.pagination import (
    LimitOffsetPagination,
    PageNumberPagination,
)
from rest_framework.response import Response
from rest_framework.settings import api_settings


class BaseLimitOffsetPagination(LimitOffsetPagination):
    """Базовый класс limit offset пагинации с валидацией на максимум."""

    default_limit = api_settings.PAGE_SIZE or 50
    max_limit = 1000
    MAX_OFFSET = 20_000

    def get_offset(self, request):
        """Добавляет проверку offset на максимум."""
        offset = super().get_offset(request)
        if offset > self.MAX_OFFSET:
            raise ValidationError(
                {'offset': f'Слишком большое значение (>{self.MAX_OFFSET}).'}
            )
        return offset


class NewsLimitOffsetPagination(BaseLimitOffsetPagination):
    """Пагинация для новостей."""

    default_limit = 6


class LiteraturePageNumberPagination(PageNumberPagination):
    """Пагинация для литературы."""

    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        """Генерирует ответ с пагинацией и дополнительными полями."""
        return Response(
            OrderedDict(
                [
                    ('count', self.page.paginator.count),
                    ('total_pages', self.page.paginator.num_pages),
                    ('current_page', self.page.number),
                    ('page_size', self.get_page_size(self.request)),
                    ('next', self.get_next_link()),
                    ('previous', self.get_previous_link()),
                    ('results', data),
                ]
            )
        )
