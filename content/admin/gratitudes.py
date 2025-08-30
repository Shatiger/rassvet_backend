"""Конфигурация админки для модели Gratitude.

Этот модуль содержит класс GratitudeAdmin,
настраивающий отображение и поведение записей благодарностей в админке.
"""

from django.contrib import admin

from content.base_models import TopOrderedModelAdmin
from content.constants import EMPTY_VALUE_DISPLAY
from content.models import Gratitude


@admin.register(Gratitude)
class GratitudeAdmin(TopOrderedModelAdmin):
    """Настройка отображения списка Gratitude и форм редактирования.

    Определяет отображаемые и редактируемые поля, фильтры, поиск и секции.
    """

    list_display = ('title', 'is_active', 'move_up_down_links')
    list_editable = ('is_active',)
    list_filter = ('is_active', 'created_at')
    search_fields = ('title',)
    readonly_fields = ('created_at', 'updated_at')
    empty_value_display = EMPTY_VALUE_DISPLAY
    fieldsets = (
        (
            'Основные данные',
            {'fields': ('title', 'file', 'is_active')},
        ),
        (
            'Системная информация',
            {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)},
        ),
    )
