"""Конфигурация админки для модели Partner.

Этот модуль содержит класс PartnersAdmin,
настраивающий отображение и поведение записей партнеров в админке.
"""

from django.contrib import admin
from django.utils.html import format_html

from content.base_models import BaseOrderedModelAdmin
from content.mixins import CharCountAdminMixin
from content.models import Partner


@admin.register(Partner)
class PartnersAdmin(CharCountAdminMixin, BaseOrderedModelAdmin):
    """Настройка отображения списка Partner с предпросмотром логотипа."""

    charcount_fields = {
        'name': 50,
        'description': 200,
    }
    list_display = ('name', 'logo_preview', 'move_up_down_links')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at', 'logo_preview')
    fieldsets = (
        (
            'Основная информация',
            {'fields': ('name', 'logo', 'description')},
        ),
        (
            'Системная информация',
            {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)},
        ),
    )

    @admin.display(description='Логотип')
    def logo_preview(self, obj):
        """Отображает превью логотипа."""
        if obj.logo:
            return format_html('<img src="{}" width="50" />', obj.logo.url)
        return '—'
