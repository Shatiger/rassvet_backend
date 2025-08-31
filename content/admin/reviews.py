"""Конфигурация админки для модели Review.

Этот модуль содержит класс ReviewAdmin,
настраивающий отображение и поведение записей партнеров в админке.
"""

from django.contrib import admin

from content.base_models import BaseOrderedModelAdmin
from content.mixins import CharCountAdminMixin
from content.models import Review


@admin.register(Review)
class ReviewAdmin(CharCountAdminMixin, BaseOrderedModelAdmin):
    """Настройка отображения списка Review и форм редактирования.

    Определяет отображаемые и редактируемые поля, фильтры, поиск и секции.
    """

    charcount_fields = {
        'author_name': 45,
        'content': 200,
    }
    list_display = ('author_name', 'is_active', 'move_up_down_links')
    list_editable = ('is_active',)
    list_filter = ('is_active', 'created_at')
    search_fields = ('content', 'author_name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (
            'Основные данные',
            {'fields': ('author_name', 'content', 'is_active')},
        ),
        (
            'Системная информация',
            {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)},
        ),
    )
