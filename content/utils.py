"""Модуль содержит утилиты и функции, связанные с Проектом.

Функции:
    1. ckeditor_function: Функция создающая text поля для моделей проекта.
"""

from django_ckeditor_5.fields import CKEditor5Field

from .validators import validate_not_empty_html


def ckeditor_function(
    verbose_name='verbose_name',
    config_name='default',
    blank=False,
    null=False,
    validators=None,
    help_text='',
):
    """Функция создающая text поля для моделей проекта."""
    return CKEditor5Field(
        verbose_name=verbose_name,
        config_name=config_name,
        blank=blank,
        null=null,
        validators=validators
        if validators is not None
        else [validate_not_empty_html],
        help_text=help_text,
    )


def html_cleaner(field, tags):
    """Используется для очистки ckeditor полей от дефолтных тегов."""
    if field == tags:
        return ''
    return field
