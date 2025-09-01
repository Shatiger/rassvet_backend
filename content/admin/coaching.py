"""Административная конфигурация для Консультации и обучение.

Этот модуль содержит:
- CoachingPhotoAdmin: Inline-класс для фотографий, прикреплённых к coaching.
- CoachingAdmin: Админ зона Coaching..
"""

from django.contrib import admin

from content.base_models import TopOrderedModelAdmin
from content.models.coaching import Coaching, CoachingPhoto


class CoachingPhotoAdmin(admin.StackedInline):
    """Inline-класс для фотографий, прикреплённых к coaching."""

    model = CoachingPhoto
    min_num = 1
    max_num = 3


@admin.register(Coaching)
class CoachingAdmin(TopOrderedModelAdmin):
    """Админ зона Coaching."""

    list_display = (
        'title',
        'date',
        'short_text',
        'move_up_down_links',
    )
    list_filter = ('date',)
    search_fields = ('date',)
    inlines = (CoachingPhotoAdmin,)
    empty_value_display = '-пусто-'

    def get_queryset(self, request):
        """Оптимизированный queryset для избежания N+1 (prefetch_related)."""
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('photos')
