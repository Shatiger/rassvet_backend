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

from .site import admin_site


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


@admin.register(TrainingAndInternships, site=admin_site)
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
        'add_info': 30,
    }
    list_display = [
        '__str__',
        'date',
        'price',
        'move_up_down_links',
    ]
    fieldsets = (
        (
            'Основная информация карточки обучения и стажировок',
            {
                'fields': (
                    'title',
                    'add_info',
                    'short_description',
                    'price',
                    'date',
                    'format_study',
                    'action_on_button',
                    'linked_news',
                ),
                'description': 'Поля для карточки Обучения и стажировок на '
                'странице "Специалистам"',
            },
        ),
        (
            'Информация для подробной страницы "Специалистам. Обучение '
            'подробная"',
            {
                'fields': ('location', 'text_block'),
                'description': 'Поля заполняемые при выборе типа перехода '
                '"Подробная страница"',
            },
        ),
    )
    inlines = [TrainingAndInternshipsPhotoInline]

    def get_queryset(self, request):
        """Возвращает queryset с предзагруженными зависимостями."""
        q_set = super().get_queryset(request)
        return q_set.prefetch_related('photos')
