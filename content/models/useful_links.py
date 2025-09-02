"""Модуль содержит модели, связанные с Полезные ссылки.

Модели:
    1. ChapterUsefulLinks: Модель разделов Полезные ссылки
    2. ArticleUsefulLinks: Модель статьи Полезные ссылки
"""

from django.db import models

from content.mixins import TitleMixin


class ChapterUsefulLinks(TitleMixin, models.Model):
    """Модель разделов Полезные ссылки."""

    class Meta:
        verbose_name = 'Раздел'
        verbose_name_plural = 'Полезные ссылки'
        ordering = ('title',)

    def __str__(self):
        """Возвращает строковое представление ChapterUsefulLinks."""
        return self.title


class ArticleUsefulLinks(TitleMixin, models.Model):
    """Модель статьи Полезные ссылки."""

    chapter = models.ForeignKey(
        ChapterUsefulLinks,
        on_delete=models.CASCADE,
        related_name='article_useful_links',
        verbose_name='Раздел Полезные ссылки',
    )
    link = models.URLField(
        verbose_name='Ссылка',
    )

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Полезные ссылки - статьи'
        ordering = ('title',)

    def __str__(self):
        """Возвращает строковое представление ArticleUsefulLinks."""
        return self.title
