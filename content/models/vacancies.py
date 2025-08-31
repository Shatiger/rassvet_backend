"""Модуль содержит модели, связанные с вакансиями.

Классы:
    RedirectChoises: Перечисление возможных статусов для типа перехода.

Модели:
    1. Vacancy: содержит информацию о вакансиях.
"""
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

from ordered_model.models import OrderedModel

from content.constants import IMAGE_CONTENT_TYPES
from content.mixins import TimestampMixin
from content.utils import ckeditor_function, html_cleaner
from content.validators import validate_not_empty_html


class Vacancy(TimestampMixin, OrderedModel):
    """Модель вакансий."""

    class RedirectChoises(models.TextChoices):
        DETAIL = 'detail', 'На страницу "Вакансии_подробная"'
        FORM = 'form', 'На форму "Форма регистрации и отклика"'

    profession = models.CharField(max_length=200, verbose_name='Профессия')
    photo = models.ImageField(
        upload_to='vacancies/photos/',
        verbose_name='Фотография',
        validators=[FileExtensionValidator(IMAGE_CONTENT_TYPES)],
    )
    salary = models.CharField(max_length=200, verbose_name='Зарплата')
    short_description = models.TextField(
        max_length=500, verbose_name='Краткий текст'
    )
    schedule = models.CharField(
        max_length=200, blank=True, verbose_name='График'
    )
    location = models.CharField(
        max_length=200, blank=True, verbose_name='Место'
    )
    redirect_type = models.CharField(
        max_length=10,
        choices=RedirectChoises.choices,
        default=RedirectChoises.DETAIL,
        verbose_name='Тип перехода',
    )
    additional_description = ckeditor_function(
        verbose_name='Дополнительное описание',
        blank=True,
        validators=[],
    )
    detailed_description = ckeditor_function(
        verbose_name='Описание вакансии', blank=True, validators=[]
    )
    external_link = models.URLField(
        blank=True, verbose_name='Ссылка на внешнюю платформу'
    )

    class Meta(OrderedModel.Meta):
        verbose_name = 'Вакансия'
        verbose_name_plural = 'Вакансии'
        ordering = ['order']
        indexes = [models.Index(fields=['order'])]

    def __str__(self):
        """Возвращает строковое представление вакансии."""
        return self.profession

    def save(self, *args, **kwargs):
        """Сохранение с валидацией и очисткой пустый ckeditor полей."""
        self.full_clean()
        self.additional_description = html_cleaner(
            self.additional_description, '<p>&nbsp;</p>'
        )
        self.detailed_description = html_cleaner(
            self.detailed_description, '<p>&nbsp;</p>'
        )
        super().save(*args, **kwargs)

    def clean(self):
        """Валидация модели."""
        super().clean()
        errors = {}
        if self.redirect_type == self.RedirectChoises.DETAIL:
            try:
                validate_not_empty_html(
                    self.additional_description,
                    'Обязательное поле при выборе '
                    '"На страницу Вакансии_подробная"',
                )
            except ValidationError as e:
                errors['additional_description'] = e.message
            try:
                validate_not_empty_html(
                    self.detailed_description,
                    'Обязательное поле при выборе '
                    '"На страницу Вакансии_подробная"',
                )
            except ValidationError as e:
                errors['detailed_description'] = e.message
        if errors:
            raise ValidationError(errors)
