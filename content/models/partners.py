"""Модуль содержит модель для работы с партнёрами.

Модели:
    - Partner: Модель для хранения информации о партнёрах
"""

from django.core.validators import FileExtensionValidator
from django.db import models
from ordered_model.models import OrderedModel

from content.constants import IMAGE_CONTENT_TYPES
from content.mixins import TimestampMixin


class Partner(TimestampMixin, OrderedModel):
    """Модель для хранения информации о партнёрах."""

    name = models.CharField(
        max_length=255,
        verbose_name='Название партнера',
    )
    logo = models.ImageField(
        upload_to='partners/logos/',
        verbose_name='Логотип партнера',
        validators=[FileExtensionValidator(IMAGE_CONTENT_TYPES)],
    )
    description = models.TextField(
        verbose_name='Описание',
    )

    class Meta(OrderedModel.Meta):
        """Мета-настройки модели Partners."""

        verbose_name = 'Партнер'
        verbose_name_plural = 'Партнеры'
        ordering = ['order']
        indexes = [models.Index(fields=['order'])]

    def __str__(self):
        """Строковое представление."""
        if len(self.name) > 50:
            return f'{self.name[:50]}...'
        return self.name
