"""Пакет поиска по сайту.

Содержит базовый индексатор, реестр индексаторов и утилиты
подготовки текста. Конкретные индексаторы моделей объявляются
в модуле indexers.
"""

from .base import BaseIndexer, SearchRegistry, registry
from .text import join_text, strip_html, truncate

__all__ = [
    'BaseIndexer',
    'SearchRegistry',
    'join_text',
    'registry',
    'strip_html',
    'truncate',
]
