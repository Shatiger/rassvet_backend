"""Административная конфигурация для Консультации и обучение.

Этот модуль содержит:
- CoachingPhotoAdmin: Inline-класс для фотографий, прикреплённых к coaching.
- CoachingAdmin: Админ зона Coaching..
"""

from django.contrib import admin

from content.base_models import TopOrderedModelAdmin
from content.mixins import CharCountAdminMixin
from content.models.coaching import Coaching

from .site import admin_site


@admin.register(Coaching, site=admin_site)
class CoachingAdmin(CharCountAdminMixin, TopOrderedModelAdmin):
    """Админ зона Coaching."""

    charcount_fields = {
        'title': 70,
        'short_description': 30,
        'short_text': 380,
        'service_price': 15,
        'date': 20,
    }
    list_display = (
        'title',
        'date',
        'service_price',
        'move_up_down_links',
    )
    fieldsets = (
        (
            'Основная информация карточки "Консультации и обучение"',
            {
                'fields': (
                    'title',
                    'photo',
                    'add_info',
                    'short_text',
                    'service_price',
                    'date',
                    'course_format',
                    'button',
                    'link_button',
                ),
            },
        ),
    )
    list_filter = ('date',)
    search_fields = ('date',)
    empty_value_display = '-пусто-'
