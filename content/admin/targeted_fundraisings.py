"""Административная конфигурация для адресных сборов и их вложенных элементов.

Этот модуль содержит:
- validate_forms: вспомогательная функция валидации инлайн-форм.
- BaseValidatedInline: базовый inline-класс с встроенной валидацией.
- FundraisingPhotoInline: inline-класс для фотографий сбора.
- FundraisingTextBlockInline: inline-класс для текстовых блоков сбора.
- TargetedFundraisingAdmin: конфигурация для модели TargetedFundraising.
"""

from django.contrib import admin
from django.core.exceptions import ValidationError
from ordered_model.admin import (
    OrderedTabularInline,
    OrderedInlineModelAdminMixin,
)

from content.base_models import BaseOrderedModelAdmin
from content.mixins import CharCountAdminMixin
from content.models import (
    FundraisingPhoto,
    TargetedFundraising,
)


def validate_forms(forms, error_detail):
    """Проверяет наличие хотя бы одной валидной формы."""
    cleaned_forms = [
        form
        for form in forms
        if form.cleaned_data and not form.cleaned_data.get('DELETE', False)
    ]
    if len(cleaned_forms) < 1:
        raise ValidationError(error_detail)


class FundraisingPhotoInline(OrderedTabularInline):
    """Inline-класс для фотографий, прикреплённых к сбору."""

    model = FundraisingPhoto
    fields = (
        'image',
        'move_up_down_links',
    )
    readonly_fields = ('move_up_down_links',)
    ordering = ('order',)
    min_num = 1
    max_num = 3

    validate_min = True
    validation_error_message = 'Должна быть как минимум одна фотография.'

    def get_queryset(self, request):
        """Возвращает queryset фотографий с подгруженным FK на сбор."""
        qs = super().get_queryset(request)
        return qs.select_related('fundraising')


@admin.register(TargetedFundraising)
class TargetedFundraisingAdmin(
    CharCountAdminMixin, OrderedInlineModelAdminMixin, BaseOrderedModelAdmin
):
    """Конфигурация админки для модели TargetedFundraising.

    Отвечает за отображение, фильтрацию, редактирование и действия для сборов.
    """

    charcount_fields = {
        'title': 60,
        'short_description': 350,
    }
    list_display = (
        'title',
        'status',
        'fundraising_link',
        'move_up_down_links',
    )
    list_editable = ('status',)
    list_filter = (
        'status',
        'created_at',
    )
    search_fields = ('title',)
    readonly_fields = (
        'created_at',
        'updated_at',
    )
    inlines = [
        FundraisingPhotoInline,
    ]
    actions = [
        'move_to_active',
        'move_to_completed',
    ]

    fieldsets = (
        (
            'Основные данные',
            {
                'fields': (
                    'title',
                    'short_description',
                    'fundraising_link',
                    'status',
                    'top_text_block',
                    'center_text_block',
                    'bottom_text_block',
                )
            },
        ),
        (
            'Системная информация',
            {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)},
        ),
    )

    def get_queryset(self, request):
        """Возвращает queryset сборов с предзагруженными зависимостями."""
        q_set = super().get_queryset(request)
        return q_set.prefetch_related(
            'photos',
        )

    @admin.action(description='Переместить в актуальные')
    def move_to_active(self, request, queryset):
        """Действие: переводит выбранные сборы в статус 'active'."""
        queryset.update(status='active')

    @admin.action(description='Переместить в завершенные')
    def move_to_completed(self, request, queryset):
        """Действие: переводит выбранные сборы в статус 'completed'."""
        queryset.update(status='completed')
