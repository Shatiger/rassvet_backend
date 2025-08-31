"""Модуль содержит модели сотрудников, документов и их типов.

Модели:
    - Employee: Содержит информацию о сотрудниках компании
    - TypeDocument: Хранит типы документов
    - Document: Хранит документы, прикрепленные к сотрудникам
"""

import html
import os

from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.html import strip_tags
from django_ckeditor_5.fields import CKEditor5Field
from ordered_model.models import OrderedModel

from content.constants import IMAGE_CONTENT_TYPES
from content.mixins import TimestampMixin
from content.validators import validate_not_empty_html


def upload_file(instance, filename):
    """Генерирует путь к файлу для загрузки."""
    return f'team/{instance.employee.id}/{filename}'


class Employee(TimestampMixin, OrderedModel):
    """Модель для хранения информации о членах команды."""

    name = models.CharField(
        max_length=100,
        verbose_name='ФИО',
    )
    image = models.ImageField(
        upload_to='team',
        verbose_name='Фото',
        validators=[FileExtensionValidator(IMAGE_CONTENT_TYPES)],
    )
    main_specialities = models.TextField(
        verbose_name='Специальности на общей странице',
    )
    interviews = models.URLField(verbose_name='Интервью', blank=True)
    specialists_register = models.URLField(
        verbose_name='Реестр специалистов', blank=True
    )
    category_on_main = models.BooleanField(
        default=False,
        verbose_name='Отображать категории документов на главной странице',
    )
    specialities = CKEditor5Field(
        verbose_name='Специальности',
        config_name='default',
        validators=[validate_not_empty_html],
    )
    education = CKEditor5Field(
        verbose_name='Образование',
        config_name='default',
        blank=True,
    )
    additional_education = CKEditor5Field(
        verbose_name='Дополнительное образование',
        config_name='default',
        blank=True,
    )
    trainings = CKEditor5Field(
        verbose_name='Пройденные тренинги',
        config_name='default',
        blank=True,
    )

    class Meta(OrderedModel.Meta):
        """Класс Meta для модели Employee, содержащий мета-данные."""

        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'
        ordering = [
            'order',
        ]
        indexes = [models.Index(fields=['order'])]

    def __str__(self):
        """Возвращает строковое представление объекта сотрудника."""
        return self.name

    def save(self, *args, **kwargs):
        """Переопределяет метод сохранения для очистки HTML-контента в полях.

        Этот метод проверяет поля additional_education и trainings на наличие
        пустого HTML-контента и очищает их перед сохранением объекта.
        """
        for field in ('additional_education', 'trainings'):
            original_field = getattr(self, field)
            setattr(self, field, self._clean_empty_html(original_field))
        super().save(*args, **kwargs)

    def _clean_empty_html(self, raw_html):
        """Очищает HTML-контент, если он пустой.

        Функция удаляет HTML-теги, возвращая пустую строку,
        если текст после очистки не содержит видимого содержания.
        """
        text = strip_tags(raw_html or '')
        text = html.unescape(text)
        return '' if not text.strip() else raw_html


class TypeDocument(models.Model):
    """Модель для хранения типов документов."""

    name = models.CharField(
        max_length=100, verbose_name='Название типа документа'
    )

    class Meta:
        """Класс Meta для модели TypeDocument, содержащий мета-данные."""

        verbose_name = 'Тип документа'
        verbose_name_plural = 'Типы документов'

    def __str__(self):
        """Возвращает строковое представление типа документа."""
        return self.name


class Document(models.Model):
    """Модель для хранения документов."""

    file = models.ImageField(
        upload_to=upload_file,
        verbose_name='Файл документа',
        validators=[FileExtensionValidator(IMAGE_CONTENT_TYPES)],
    )
    type = models.ForeignKey(
        TypeDocument,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name='documents',
        verbose_name='Тип документа',
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='Сотрудник',
    )
    on_main_page = models.BooleanField(
        default=False, verbose_name='Отображать в ленте'
    )

    class Meta:
        """Класс Meta для модели Document, содержащий мета-данные."""

        verbose_name = 'Документ'
        verbose_name_plural = 'Дипломы и сертификаты'
        ordering = ['employee__name', 'type__name', 'file']

    def __str__(self):
        """Возвращает строковое представление документа."""
        filename = os.path.basename(self.file.name or '')
        parts = [
            self.employee.name if self.employee_id else 'без сотрудника',
            self.type.name if self.type_id else 'без типа',
            filename or 'без файла',
        ]
        return ' — '.join(parts)
