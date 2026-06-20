"""Модуль содержит модель для работы с отзывами.

Модели:
    - Review: Модель для хранения информации об отзывах
"""

from django.db import models
from ordered_model.models import OrderedModel

from content.mixins import TimestampMixin


class Review(TimestampMixin, OrderedModel):
    """Модель для хранения информации об отзывах."""

    author_name = models.CharField(
        'Автор',
        max_length=100,
    )
    content = models.TextField('Текст отзыва')
    is_active = models.BooleanField('Активный', default=True)

    class Meta(OrderedModel.Meta):
        """Класс Meta для модели Review, содержащий мета-данные."""

        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = [
            'order',
        ]
        indexes = [models.Index(fields=['order'])]

    def __str__(self):
        """Строковое представление."""
        if len(self.author_name) > 50:
            return f'{self.author_name[:50]}...'
        return self.author_name
