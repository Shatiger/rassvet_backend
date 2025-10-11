"""Административная конфигурация для Полезные ссылки.

Этот модуль содержит:
- ArticleUsefulLinksInline: Inline-класс для статьи Полезные ссылки.
- ChapterUsefulLinksAdmin: Админ зона разделов Полезные ссылки.
"""

from django.contrib import admin

from content.mixins import (
    InstantDeleteInlineMixin,
    InstantDeleteSingleModelAdminMixin,
)
from content.models import ArticleUsefulLinks, ChapterUsefulLinks

from .site import admin_site


class ArticleUsefulLinksInline(InstantDeleteInlineMixin, admin.StackedInline):
    """Inline-класс для статьи Полезные ссылки."""

    model = ArticleUsefulLinks
    min_num = 1
    show_change_link = True


@admin.register(ChapterUsefulLinks, site=admin_site)
class ChapterUsefulLinksAdmin(
    InstantDeleteSingleModelAdminMixin, admin.ModelAdmin
):
    """Админ зона разделов Полезные ссылки."""

    instant_delete_model = ArticleUsefulLinks
    list_display = ('title',)
    search_fields = ('title',)
    inlines = (ArticleUsefulLinksInline,)

    def get_queryset(self, request):
        """Возвращает queryset с предзагруженными зависимостями."""
        q_set = super().get_queryset(request)
        return q_set.prefetch_related('article_useful_links')
