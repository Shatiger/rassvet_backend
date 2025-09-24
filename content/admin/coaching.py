"""Административная конфигурация для Консультации и обучение.

Этот модуль содержит:
- CoachingPhotoAdmin: Inline-класс для фотографий, прикреплённых к coaching.
- CoachingAdmin: Админ зона Coaching..
"""

from django.contrib import admin

from content.base_models import TopOrderedModelAdmin
from content.mixins import CharCountAdminMixin
from content.models.coaching import Coaching, CoachingPhoto


class CoachingPhotoAdmin(admin.StackedInline):
    """Inline-класс для фотографий, прикреплённых к coaching."""

    model = CoachingPhoto
    min_num = 1
    max_num = 3


@admin.register(Coaching)
class CoachingAdmin(CharCountAdminMixin, TopOrderedModelAdmin):
    """Админ зона Coaching."""

    charcount_fields = {
        'title': 70,
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
                    'short_text',
                    'service_price',
                    'course_format',
                    'date',
                    'button',
                ),
            },
        ),
    )
    list_filter = ('date',)
    search_fields = ('date',)
    inlines = (CoachingPhotoAdmin,)
    empty_value_display = '-пусто-'

    def get_queryset(self, request):
        """Оптимизированный queryset для избежания N+1 (prefetch_related)."""
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('photos')
