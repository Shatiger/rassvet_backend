"""Модуль содержит модели, связанные с адресными сборами.

Классы:
    FundraisingStatus: Перечисление возможных статусов для адресного сбора.

Модели:
    1. TargetedFundraising: Модель для хранения информации об адресном сборе
    2. FundraisingPhoto: Модель для хранения фотографий адресных сборов
    3. FundraisingTextBlock: Модель для хранения текстовых блоков
       адресных сборов
"""

from django.core.validators import (
    FileExtensionValidator,
)
from django.db import models

from ordered_model.models import OrderedModel

from content.constants import IMAGE_CONTENT_TYPES
from content.mixins import TimestampMixin, TitleMixin

from content.utils import ckeditor_function


def upload_file(instance, filename):
    """Генерирует путь к файлу для загрузки."""
    return f'fundraisings/{instance.fundraising.id}/{filename}'


class FundraisingStatus(models.TextChoices):
    """Класс, определяющий возможные статусы адресного сбора."""

    ACTIVE = 'active', 'Актуальный сбор'
    COMPLETED = 'completed', 'Завершенный сбор'


class TargetedFundraising(
    TitleMixin,
    TimestampMixin,
    OrderedModel,
):
    """Модель для хранения информации об адресных сборах."""

    short_description = models.TextField(
        verbose_name='Краткое описание',
    )
    fundraising_link = models.URLField('Ссылка на сбор')
    status = models.CharField(
        max_length=max(len(value) for value, _ in FundraisingStatus.choices),
        choices=FundraisingStatus.choices,
        default=FundraisingStatus.ACTIVE,
        verbose_name='Статус сбора',
    )
    top_text_block = ckeditor_function(
        verbose_name='Верхний текстовый блок',
        blank=True,
        null=True,
        validators=[],
        help_text='Рекомендованное количество символов - 370',
    )
    center_text_block = ckeditor_function(
        verbose_name='Центральный текстовый блок',
    )
    bottom_text_block = ckeditor_function(
        verbose_name='Нижний текстовый блок',
        blank=True,
        null=True,
        validators=[],
        help_text='Рекомендованное количество символов - 290',
    )

    class Meta(OrderedModel.Meta):
        """Класс Meta для TargetedFundraising, содержащий мета-данные."""

        verbose_name = 'Адресный сбор'
        verbose_name_plural = 'Адресные сборы'
        ordering = [
            'order',
        ]

    def save(self, *args, **kwargs):
        """Переопределяет метод сохранения для очистки HTML-контента в полях.

        Этот метод проверяет поля на наличие
        пустого HTML-контента и присваивает None.
        """
        if self.top_text_block == '<p>&nbsp;</p>':
            self.top_text_block = ''
        if self.bottom_text_block == '<p>&nbsp;</p>':
            self.bottom_text_block = ''
        super().save(*args, **kwargs)


class FundraisingPhoto(OrderedModel):
    """Модель для хранения информации о фотографиях адресных сборов."""

    fundraising = models.ForeignKey(
        TargetedFundraising,
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name='Адресный сбор',
    )
    image = models.ImageField(
        upload_to=upload_file,
        verbose_name='Фотография',
        validators=[FileExtensionValidator(IMAGE_CONTENT_TYPES)],
    )
    order_with_respect_to = 'fundraising'

    class Meta(OrderedModel.Meta):
        """Класс Meta для FundraisingPhoto, содержащий мета-данные."""

        verbose_name = 'Фотография сбора'
        verbose_name_plural = 'Фотографии сборов'
        ordering = [
            'order',
        ]
        indexes = [
            models.Index(fields=['fundraising', 'order']),
        ]

    def __str__(self):
        """Возвращает строковое представление фотографии."""
        return f'Фотография для {self.fundraising.title}'
