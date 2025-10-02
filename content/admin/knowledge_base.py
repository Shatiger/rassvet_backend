"""Административная конфигурация для Базы Знаний.

Этот модуль содержит:
- ArticleGallerykAdmin: Inline-класс для Галерея фото.
- ArticleTextBlockAdmin: Inline-класс для Текстовый блок.
- ChapterKnowledgeBaseAdmin: Админ зона разделов Базы знаний.
- ArticleAdmin: Админ зона статьи Базы знаний.
"""

from django.contrib import admin

from content.models import (
    Article,
    ArticleGallery,
    ArticleTextBlock,
    ArticleVideoLink,
    ChapterKnowledgeBase,
)


@admin.register(ChapterKnowledgeBase)
class ChapterKnowledgeBaseAdmin(admin.ModelAdmin):
    """Админ зона разделов Базы знаний."""

    list_display = ('title',)
    search_fields = ('title',)


class ArticleGallerykAdmin(admin.StackedInline):
    """Inline-класс для Галерея фото статьи Базы знаний."""

    model = ArticleGallery
    extra = 1
    min_num = 0
    max_num = 255

    def get_queryset(self, request):
        """Оптимизация запросов к базе данных."""
        qs = super().get_queryset(request)
        return qs.select_related('article')


class ArticleTextBlockAdmin(admin.StackedInline):
    """Inline-класс для Текстовый блок статьи Базы знаний."""

    model = ArticleTextBlock
    extra = 1
    min_num = 0
    max_num = 255


class ArticleVideoLinkAdmin(admin.StackedInline):
    """Inline-класс для Ссылка на видео статьи Базы знаний."""

    model = ArticleVideoLink
    extra = 1
    min_num = 0
    max_num = 255


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """Админ зона статьи Базы знаний."""

    list_display = (
        'title',
        'chapter',
    )
    list_filter = ('chapter',)
    search_fields = ('title',)
    inlines = (
        ArticleTextBlockAdmin,
        ArticleVideoLinkAdmin,
        ArticleGallerykAdmin,
    )

    def get_queryset(self, request):
        """Оптимизация запросов к базе данных."""
        qs = super().get_queryset(request)
        return qs.select_related('chapter')
