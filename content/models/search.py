"""Модуль содержит модели, связанные с поиском по сайту.

Модели:
    1. SearchEntry: Денормализованная запись поискового индекса

Перечисления:
    1. SearchEntityType: Типы сущностей, попадающие в индекс
"""

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models

from content.constants import (
    SEARCH_ENTITY_TYPE_LENGTH,
    SEARCH_EXTERNAL_URL_LENGTH,
    TITLE_LENGTH,
)
from content.mixins import TimestampMixin


class SearchEntityType(models.TextChoices):
    """Типы сущностей, попадающие в поисковый индекс.

    Значение используется фронтендом для сборки ссылки на объект,
    поэтому переименование кода является ломающим изменением.
    """

    NEWS = 'news', 'Новость'
    ARTICLE = 'article', 'Статья базы знаний'
    PROJECT = 'project', 'Проект'
    VACANCY = 'vacancy', 'Вакансия'
    TRAINING = 'training', 'Обучение и стажировки'
    FUNDRAISING = 'fundraising', 'Адресный сбор'
    EMPLOYEE = 'employee', 'Сотрудник'
    LITERATURE = 'literature', 'Литература'
    PARTNER = 'partner', 'Партнёр'
    REVIEW = 'review', 'Отзыв'
    GRATITUDE = 'gratitude', 'Благодарность'
    USEFUL_LINK = 'useful_link', 'Полезная ссылка'
    REPORT = 'report', 'Документы и отчёты'
    COACHING = 'coaching', 'Консультация и обучение'
    MISSION = 'mission', 'Миссия'
    SUPERVISOR = 'supervisor', 'Супервизор'


class SearchEntry(TimestampMixin, models.Model):
    """Денормализованная запись поискового индекса.

    Одна запись соответствует одному объекту индексируемой модели.
    Наполняется командой reindex_search и сигналами, вручную
    не редактируется.

    Ссылка на страницу сайта намеренно не хранится: фронтенд собирает
    путь по паре entity_type и object_id, поэтому изменение роутинга
    не требует переиндексации. В external_url попадают только ссылки
    на внешние ресурсы.
    """

    entity_type = models.CharField(
        'Тип сущности',
        max_length=SEARCH_ENTITY_TYPE_LENGTH,
        choices=SearchEntityType.choices,
        db_index=True,
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name='Тип контента',
        related_name='search_entries',
    )
    object_id = models.PositiveIntegerField('ID объекта')
    content_object = GenericForeignKey('content_type', 'object_id')
    title = models.CharField('Заголовок', max_length=TITLE_LENGTH)
    body = models.TextField(
        'Текст для поиска',
        blank=True,
        help_text='Текст, очищенный от HTML-разметки.',
    )
    external_url = models.CharField(
        'Внешняя ссылка',
        max_length=SEARCH_EXTERNAL_URL_LENGTH,
        blank=True,
        help_text='Заполняется, если объект ведёт на внешний ресурс. '
        'Значение производное, валидируется на исходной модели.',
    )
    published_at = models.DateField(
        'Дата публикации',
        null=True,
        blank=True,
        help_text='Используется для сортировки при равном ранге.',
    )
    search_vector = SearchVectorField(
        'Поисковый вектор',
        null=True,
        editable=False,
    )

    class Meta:
        """Мета-настройки модели SearchEntry."""

        ordering = ['id']
        verbose_name = 'Запись поискового индекса'
        verbose_name_plural = 'Записи поискового индекса'
        constraints = [
            models.UniqueConstraint(
                fields=['content_type', 'object_id'],
                name='unique_search_entry_object',
            ),
        ]
        indexes = [
            GinIndex(
                fields=['search_vector'],
                name='search_vector_gin_idx',
            ),
            GinIndex(
                fields=['title'],
                name='search_title_trgm_idx',
                opclasses=['gin_trgm_ops'],
            ),
            models.Index(
                fields=['entity_type', '-published_at'],
                name='search_type_published_idx',
            ),
        ]

    def __str__(self):
        """Строковое представление записи индекса."""
        title = self.title[:50]
        return f'{self.get_entity_type_display()}: {title}'
