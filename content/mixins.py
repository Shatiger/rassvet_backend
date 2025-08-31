"""Модуль содержит миксины для классов."""

from typing import Optional, Type

from django.contrib import admin
from django.db import models

from rest_framework.serializers import Serializer

from .constants import ORDER_DEFAULT, TITLE_LENGTH


class TitleMixin(models.Model):
    """Абстрактная модель для добавления поля заголовка."""

    title = models.CharField('Заголовок', max_length=TITLE_LENGTH)

    class Meta:
        """Мета-класс для указания того, что модель является абстрактной."""

        abstract = True


class TimestampMixin(models.Model):
    """Абстрактная модель для добавления временных меток."""

    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        """Мета-класс для указания того, что модель является абстрактной."""

        abstract = True


class OrderMixin(models.Model):
    """Абстрактная модель для добавления поля порядка отображения."""

    order = models.PositiveSmallIntegerField(
        'Порядок отображения',
        default=ORDER_DEFAULT,
        help_text='Чем меньше значение, тем первее в списке',
    )

    class Meta:
        """Мета-класс для указания того, что модель является абстрактной."""

        abstract = True


class CleanEmptyHTMLMixin:
    """Миксин для автоматической очистки HTML-полей от "пустых" значений."""

    clean_html_fields: tuple[str, ...] = ()

    def save(self, *args, **kwargs):
        """Переопределяет сохранение объекта: очищает указанные HTML-поля."""
        for field in self.clean_html_fields:
            original_field = getattr(self, field, None)
            setattr(self, field, self._clean_empty_html(original_field))
        super().save(*args, **kwargs)

    def _clean_empty_html(self, raw_html):
        """Проверяет значение HTML-поля.

        Если значение поля ровно <p>&nbsp;</p> (или <p> </p>), возвращает None.
        В остальных случаях возвращает оригинальное значение.
        """
        if raw_html is None:
            return None
        cleared = raw_html.strip().replace('\xa0', '&nbsp;')
        if cleared == '<p>&nbsp;</p>':
            return None
        return raw_html


class MultiSerializerViewSetMixin:
    """Миксин для выбора подходящего сериализатора из `serializer_classes`."""

    serializer_classes: Optional[dict[str, Type[Serializer]]] = None

    def get_serializer_class(self):
        """Выбирает сериализатор из словаря по действию."""
        try:
            return self.serializer_classes[self.action]
        except (KeyError, TypeError):
            return super().get_serializer_class()


class CharCountAdminMixin(admin.ModelAdmin):
    """Миксин для Django Admin, добавляющий подсчёт символов."""

    charcount_fields: dict[str, int | dict[str, int]] = {}

    class Media:
        js = ('custom_admin/js/char_count.js',)
        css = {'all': ('custom_admin/css/char_count.css',)}

    def get_form(self, request, obj=None, **kwargs):
        """Переопределяет метод get_form.

        Позволяет:
        1. Проставить data-атрибуты в HTML-виджетах выбранных полей.
        2. Добавить help_text с рекомендациями по количеству символов.
        """
        form = super().get_form(request, obj, **kwargs)
        cfg = getattr(self, 'charcount_fields', {}) or {}

        for name, limits in cfg.items():
            if name not in form.base_fields:
                continue
            base_field = form.base_fields[name]
            base_field.widget.attrs['data-charcount'] = '1'

            min_value = max_value = None
            if isinstance(limits, int):
                max_value = limits
            elif isinstance(limits, dict):
                min_value = limits.get('min')
                max_value = limits.get('max')

            if min_value is not None:
                base_field.widget.attrs['data-min'] = str(min_value)
            if max_value is not None:
                base_field.widget.attrs['data-max'] = str(max_value)

        return form
