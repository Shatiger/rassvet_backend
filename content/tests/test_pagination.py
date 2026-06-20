"""Тесты кастомной пагинации content.pagination."""

from django.test import TestCase
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request

from content.pagination import BaseLimitOffsetPagination


class BaseLimitOffsetPaginationTests(TestCase):
    """Тесты валидации offset в BaseLimitOffsetPagination."""

    def setUp(self):
        """Готовит фабрику запросов и экземпляр пагинатора."""
        self.factory = APIRequestFactory()
        self.paginator = BaseLimitOffsetPagination()

    def _request(self, **params):
        """Создаёт DRF-запрос с переданными query-параметрами."""
        return Request(self.factory.get('/', params))

    def test_offset_within_limit_ok(self):
        """Offset в пределах MAX_OFFSET принимается."""
        request = self._request(offset=100)
        self.assertEqual(self.paginator.get_offset(request), 100)

    def test_offset_above_max_raises(self):
        """Offset больше MAX_OFFSET вызывает ValidationError."""
        request = self._request(
            offset=BaseLimitOffsetPagination.MAX_OFFSET + 1
        )
        with self.assertRaises(ValidationError):
            self.paginator.get_offset(request)

    def test_max_limit_configured(self):
        """Максимальный limit ограничен значением max_limit."""
        self.assertEqual(BaseLimitOffsetPagination.max_limit, 1000)
