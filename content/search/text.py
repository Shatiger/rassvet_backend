"""Модуль подготовки текста для поискового индекса.

Функции:
    1. strip_html: Превращает HTML-разметку в плоский текст
    2. join_text: Склеивает фрагменты текста для поля body
    3. truncate: Обрезает строку до допустимой длины
"""

import html
import re

from django.utils.html import strip_tags

TAG_RE = re.compile(r'<[^>]*>')
"""Любой HTML-тег."""

WHITESPACE_RE = re.compile(r'[^\S\n]+')
"""Пробельные символы, кроме перевода строки."""

SPACED_NEWLINE_RE = re.compile(r' *\n *')
"""Перевод строки, окружённый пробелами."""

BLANK_LINES_RE = re.compile(r'\n{2,}')
"""Два и более подряд идущих перевода строки."""

BODY_SEPARATOR = '\n'
"""Разделитель фрагментов текста в поле body."""


def strip_html(value: str | None) -> str:
    """Превращает HTML-разметку в плоский текст.

    Теги заменяются на пробел, а не удаляются: django.utils.html.strip_tags
    склеивает слова на границах блоков, превращая
    '<p>детям</p><p>помощь</p>' в 'детямпомощь'. Такой текст ломает
    и токенизацию поискового вектора, и сниппеты в выдаче.

    После замены тегов HTML-сущности раскодируются, поэтому &nbsp;
    и &laquo; не попадают в индекс.
    """
    text = TAG_RE.sub(' ', value or '')
    text = strip_tags(text)
    text = html.unescape(text)
    text = WHITESPACE_RE.sub(' ', text)
    text = SPACED_NEWLINE_RE.sub('\n', text)
    return BLANK_LINES_RE.sub('\n', text).strip()


def join_text(
    parts: tuple[str | None, ...] | list[str | None],
    separator: str = BODY_SEPARATOR,
) -> str:
    """Склеивает непустые фрагменты текста, очищая каждый от HTML."""
    cleaned = (strip_html(part) for part in parts)
    return separator.join(part for part in cleaned if part)


def truncate(value: str, max_length: int) -> str:
    """Обрезает строку до max_length символов."""
    if len(value) <= max_length:
        return value
    return value[:max_length].rstrip()
