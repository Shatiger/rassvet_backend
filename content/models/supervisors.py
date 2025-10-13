from django.core.validators import FileExtensionValidator
from django.db import models

from ordered_model.models import OrderedModel

from content.constants import IMAGE_CONTENT_TYPES
from content.mixins import TimestampMixin

from . import Direction


class Supervisor(TimestampMixin, OrderedModel):
    """Модель для хранения информации о Супервизоров центра."""

    name = models.CharField(max_length=255, verbose_name='ФИО')
    image = models.ImageField(
        upload_to='supervisors/',
        verbose_name='Фото',
        validators=[FileExtensionValidator(IMAGE_CONTENT_TYPES)],
    )
    position = models.CharField(max_length=255, verbose_name='Должность')
    directions = models.ManyToManyField(
        Direction,
        verbose_name='Направление деятельности',
        related_name='supervisors',
    )

    class Meta:
        verbose_name = 'Супервизор'
        verbose_name_plural = 'Супервизоры'
        ordering = [
            'order',
        ]
        indexes = [models.Index(fields=['order'])]

    def __str__(self):
        """Строковое представление."""
        if len(self.name) > 50:
            return f'{self.name[:50]}...'
        return self.name
