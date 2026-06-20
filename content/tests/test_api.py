"""Интеграционные тесты публичного API content.

Проверяют ключевое поведение read-only эндпоинтов:
- фильтрацию по is_active (скрытые объекты не отдаются);
- solo-эндпоинт Mission (создаётся и возвращается единственный объект);
- пагинацию новостей и расчёт min_year/max_year.
"""

import datetime
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APITestCase

from content.models import Gratitude, News

PNG_BYTES = (
    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
    b'\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01'
    b'\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
)


def make_image(name='test.png'):
    """Возвращает загружаемый файл-изображение для ImageField."""
    return SimpleUploadedFile(name, PNG_BYTES, content_type='image/png')


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class GratitudeApiTests(APITestCase):
    """Тесты эндпоинта благодарностей."""

    @classmethod
    def setUpTestData(cls):
        """Создаёт активную и скрытую благодарности."""
        cls.active = Gratitude.objects.create(
            title='Активная', file=make_image(), is_active=True
        )
        cls.inactive = Gratitude.objects.create(
            title='Скрытая', file=make_image(), is_active=False
        )

    def test_list_returns_only_active(self):
        """В списке отдаются только активные благодарности."""
        response = self.client.get(reverse('gratitude-list'))
        self.assertEqual(response.status_code, 200)
        ids = [item['id'] for item in response.data['results']]
        self.assertIn(self.active.id, ids)
        self.assertNotIn(self.inactive.id, ids)

    def test_retrieve_active(self):
        """Активную благодарность можно получить по ID."""
        url = reverse('gratitude-detail', args=[self.active.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], self.active.id)


class MissionApiTests(APITestCase):
    """Тесты solo-эндпоинта Mission."""

    def test_list_creates_and_returns_solo(self):
        """Эндпоинт создаёт единственную миссию и возвращает 200."""
        response = self.client.get(reverse('mission-list'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, dict)


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class NewsApiTests(APITestCase):
    """Тесты списка новостей: пагинация и границы по годам."""

    DEFAULT_LIMIT = 6

    @classmethod
    def setUpTestData(cls):
        """Создаёт восемь новостей за разные годы."""
        years = [2020, 2021, 2022, 2023, 2024, 2025, 2026, 2019]
        for i, year in enumerate(years):
            News.objects.create(
                title=f'Новость {i}',
                photo=make_image(f'news_{i}.png'),
                summary='Краткое описание',
                date=datetime.date(year, 1, 1),
            )

    def test_default_pagination_limit(self):
        """По умолчанию выдаётся не больше default_limit новостей."""
        response = self.client.get(reverse('news-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), self.DEFAULT_LIMIT)
        self.assertEqual(response.data['count'], 8)

    def test_min_max_year_in_response(self):
        """Ответ содержит корректные min_year и max_year."""
        response = self.client.get(reverse('news-list'))
        self.assertEqual(response.data['min_year'], 2019)
        self.assertEqual(response.data['max_year'], 2026)
