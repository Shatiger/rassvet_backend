"""Модуль содержит базовый индексатор и реестр индексаторов поиска.

Классы:
    1. BaseIndexer: Базовый адаптер индексации модели
    2. SearchRegistry: Реестр индексаторов

Объекты:
    1. registry: Единственный экземпляр реестра
"""

from datetime import date, datetime

from django.core.exceptions import ImproperlyConfigured
from django.db import models

from content.constants import TITLE_LENGTH
from content.models.search import SearchEntityType

from .text import join_text, strip_html, truncate


class BaseIndexer:
    """Базовый адаптер индексации модели для поиска.

    Наследник обязан задать model и entity_type. Простые модели
    описываются только атрибутами title_field, body_fields
    и published_at_field, для остальных переопределяются
    соответствующие методы.
    """

    model: type[models.Model] | None = None
    """Индексируемая модель."""

    entity_type: str = ''
    """Код типа сущности из SearchEntityType."""

    title_field: str = 'title'
    """Поле модели, попадающее в заголовок записи индекса."""

    body_fields: tuple[str, ...] = ()
    """Поля модели, попадающие в текст записи индекса."""

    published_at_field: str | None = None
    """Поле модели с датой публикации, если она есть."""

    def get_queryset(self) -> models.QuerySet:
        """Возвращает объекты, подлежащие индексации.

        Переопределяется, если часть объектов скрыта от посетителей
        или требуется select_related и prefetch_related.
        """
        return self.model._default_manager.all()

    def get_title(self, obj) -> str:
        """Возвращает заголовок записи индекса."""
        return strip_html(getattr(obj, self.title_field, '') or '')

    def get_body(self, obj) -> str:
        """Возвращает текст записи индекса, очищенный от HTML."""
        return join_text([getattr(obj, name, '') for name in self.body_fields])

    def get_published_at(self, obj) -> date | None:
        """Возвращает дату публикации объекта или None."""
        if not self.published_at_field:
            return None
        value = getattr(obj, self.published_at_field, None)
        if isinstance(value, datetime):
            return value.date()
        return value

    def get_external_url(self, obj) -> str:
        """Возвращает ссылку на внешний ресурс или пустую строку.

        Переопределяется у моделей, которые могут вести не на страницу
        сайта, а на сторонний ресурс.
        """
        return ''

    def build_fields(self, obj) -> dict:
        """Собирает значения полей SearchEntry для объекта.

        Поле search_vector здесь не заполняется: оно вычисляется
        на стороне PostgreSQL после записи строки.
        """
        return {
            'entity_type': self.entity_type,
            'title': truncate(self.get_title(obj), TITLE_LENGTH),
            'body': self.get_body(obj),
            'external_url': self.get_external_url(obj) or '',
            'published_at': self.get_published_at(obj),
        }


class SearchRegistry:
    """Реестр индексаторов поиска.

    Хранит по одному индексатору на модель и позволяет найти его
    по модели, экземпляру или коду типа сущности.
    """

    def __init__(self):
        """Создаёт пустой реестр."""
        self._indexers: dict[type[models.Model], BaseIndexer] = {}

    def register(self, indexer_cls: type[BaseIndexer]):
        """Регистрирует индексатор, проверяя корректность настроек.

        Используется как декоратор класса и возвращает его без изменений.
        """
        name = indexer_cls.__name__
        if indexer_cls.model is None:
            raise ImproperlyConfigured(f'{name}: не задан атрибут model.')
        if indexer_cls.entity_type not in SearchEntityType.values:
            raise ImproperlyConfigured(
                f'{name}: entity_type "{indexer_cls.entity_type}" '
                'отсутствует в SearchEntityType.'
            )
        if indexer_cls.model in self._indexers:
            registered = type(self._indexers[indexer_cls.model]).__name__
            raise ImproperlyConfigured(
                f'{name}: модель {indexer_cls.model.__name__} уже '
                f'зарегистрирована в {registered}.'
            )
        duplicate = self.get_by_entity_type(indexer_cls.entity_type)
        if duplicate is not None:
            raise ImproperlyConfigured(
                f'{name}: entity_type "{indexer_cls.entity_type}" уже '
                f'занят индексатором {type(duplicate).__name__}.'
            )
        self._indexers[indexer_cls.model] = indexer_cls()
        return indexer_cls

    def get_for_model(self, model) -> BaseIndexer | None:
        """Возвращает индексатор модели или None."""
        return self._indexers.get(model)

    def get_for_instance(self, instance) -> BaseIndexer | None:
        """Возвращает индексатор объекта или None."""
        return self.get_for_model(type(instance))

    def get_by_entity_type(self, entity_type: str) -> BaseIndexer | None:
        """Возвращает индексатор по коду типа сущности или None."""
        for indexer in self._indexers.values():
            if indexer.entity_type == entity_type:
                return indexer
        return None

    @property
    def indexers(self) -> tuple[BaseIndexer, ...]:
        """Все зарегистрированные индексаторы."""
        return tuple(self._indexers.values())

    @property
    def models(self) -> tuple[type[models.Model], ...]:
        """Все зарегистрированные модели."""
        return tuple(self._indexers)

    @property
    def entity_types(self) -> tuple[str, ...]:
        """Коды типов сущностей всех зарегистрированных индексаторов."""
        return tuple(
            indexer.entity_type for indexer in self._indexers.values()
        )


registry = SearchRegistry()
"""Единственный экземпляр реестра индексаторов."""
