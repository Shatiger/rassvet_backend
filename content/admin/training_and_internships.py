"""Административная конфигурация для обучений и стажировок.

Этот модуль содержит:
- TrainingAndInternshipsAdmin: конфигурация для модели TrainingAndInternships.
- TrainingAndInternshipsPhotoInline: inline-класс для фотографий.
"""

from django.contrib import admin
from ordered_model.admin import (
    OrderedTabularInline,
    OrderedInlineModelAdminMixin,
)

from content.base_models import TopOrderedModelAdmin
from content.mixins import CharCountAdminMixin
from content.models.training_and_internships import (
    TrainingAndInternships,
    TrainingAndInternshipsPhoto,
)


class TrainingAndInternshipsPhotoInline(OrderedTabularInline):
    """Inline-класс для фотографий."""

    model = TrainingAndInternshipsPhoto
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


@admin.register(TrainingAndInternships)
class TrainingAndInternshipsAdmin(
    CharCountAdminMixin,
    OrderedInlineModelAdminMixin,
    TopOrderedModelAdmin,
):
    """Конфигурация админки для модели TrainingAndInternships."""

    charcount_fields = {
        'title': 70,
        'short_description': 380,
        'price': 15,
        'date': 20,
    }
    list_display = [
        'title',
        'date',
        'price',
        'move_up_down_links',
    ]
    inlines = [TrainingAndInternshipsPhotoInline]
    fieldsets = (
        (
            'Основные данные',
            {
                'fields': (
                    'title',
                    'short_description',
                    'price',
                    'format_study',
                    'date',
                    'action_on_button',
                    'linked_news',
                    'location',
                    'text_block',
                )
            },
        ),
    )

    def get_queryset(self, request):
        """Возвращает queryset с предзагруженными зависимостями."""
        q_set = super().get_queryset(request)
        return q_set.prefetch_related('photos')
