"""Модуль содержит модели, связанные с Литературой.

Модели:
    1. Literature: Модель литературы
"""

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models

from ordered_model.models import OrderedModel

from content.constants import IMAGE_CONTENT_TYPES, LITERATURE_CONTENT_TYPES
from content.mixins import TitleMixin
from content.utils import ckeditor_function, html_cleaner


class Literature(TitleMixin, OrderedModel):
    """Модель литературы."""

    class LinkChoises(models.TextChoices):
        FILE = 'file', 'Прикрепить файл'
        LINK = 'link', 'Прикрепить ссылку'

    author = models.CharField(max_length=255, verbose_name='Автор(ы)')
    publication_year = models.PositiveSmallIntegerField(
        default=2000,
        verbose_name='Год издания',
    )
    cover = models.ImageField(
        verbose_name='Обложка',
        validators=[FileExtensionValidator(IMAGE_CONTENT_TYPES)],
    )
    description = ckeditor_function(
        verbose_name='Описание',
        blank=True,
        validators=[],
    )
    button_type = models.CharField(
        blank=True,
        max_length=max(len(value) for value, _ in LinkChoises.choices),
        choices=LinkChoises.choices,
        verbose_name='Тип кнопки',
    )
    file = models.FileField(
        blank=True,
        verbose_name='Файл литературы',
        validators=[FileExtensionValidator(LITERATURE_CONTENT_TYPES)],
    )
    literature_url = models.URLField(
        blank=True,
        verbose_name='Ссылка на литературу',
    )

    class Meta(OrderedModel.Meta):
        verbose_name = 'Литература'
        verbose_name_plural = 'Литература'
        ordering = ['order']
        indexes = [models.Index(fields=['order'])]

    def save(self, *args, **kwargs):
        """Сохранение с валидацией и очисткой пустых ckeditor полей."""
        self.full_clean()
        self.description = html_cleaner(self.description, '<p>&nbsp;</p>')
        super().save(*args, **kwargs)

    def clean(self):
        """Валидация полей в зависимости от типа кнопки."""
        super().clean()
        errors = {}
        if self.button_type == self.LinkChoises.FILE and not self.file:
            errors['file'] = 'Добавьте файл для загрузки.'
        if (
            self.button_type == self.LinkChoises.LINK
            and not self.literature_url
        ):
            errors['literature_url'] = 'Укажите ссылку на внешнюю страницу.'
        if errors:
            raise ValidationError(errors)
