"""Модуль содержит модель для работы с отчётами.

Модели:
    - Report: Модель для хранения информации об отчётах
    - Chapter: Модель для хранения информации о разделах отчётов
"""

from django.core.validators import FileExtensionValidator
from django.db import models

from content.mixins import TitleMixin
from ordered_model.models import OrderedModel

from content.constants import FILE_CONTENT_TYPES


def upload_file(instance, filename):
    """Метод для генерации пути к файлу."""
    return f'reports/{instance.chapter.id}/{filename}'


class Chapter(TitleMixin, OrderedModel):
    """Модель для хранения информации о разделах отчетов."""

    class Meta(OrderedModel.Meta):
        """Мета-настройки модели Chapter."""

        ordering = ['order']
        indexes = [models.Index(fields=['order'])]
        verbose_name = 'Документы и отчеты'
        verbose_name_plural = 'Документы и отчеты'


class Report(TitleMixin, OrderedModel):
    """Модель для хранения информации о отчетах."""

    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.CASCADE,
        related_name='reports',
        verbose_name='Раздел',
    )
    file = models.FileField(
        upload_to=upload_file,
        verbose_name='Файл отчета',
        validators=[FileExtensionValidator(FILE_CONTENT_TYPES)],
    )
    download_icon = models.BooleanField(
        default=True, verbose_name='Иконка скачивания'
    )
    order_with_respect_to = 'chapter'

    class Meta(OrderedModel.Meta):
        """Мета-настройки модели Report."""

        indexes = [
            models.Index(fields=['chapter', 'order']),
        ]
        verbose_name = 'Отчет'
        verbose_name_plural = 'Отчеты'
