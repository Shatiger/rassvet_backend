"""Константы приложения content."""

TITLE_LENGTH = 255
"""Максимальная длина заголовка."""

CHAR_FIELD_LENGTH = 255
"""Максимальная длина поля CharField."""

ORDER_DEFAULT = 0
"""Значение по умолчанию для порядка отображения элементов."""

IMAGE_CONTENT_TYPES = [
    'jpg',
    'jpeg',
    'png',
    'webp',
    'jfif',
]
"""Формат загрузки файлов для ImageField."""

FILE_CONTENT_TYPES = ['pdf']
"""Формат загрузки файлов для FileField."""

EMPTY_VALUE_DISPLAY = '-пусто-'
"""Отображение пустого поля."""

LITERATURE_CONTENT_TYPES = [
    'pdf',
    'epub',
    'mobi',
    'azw',
    'azw3',
    'fb2',
    'djvu',
    'txt',
    'rtf',
    'doc',
    'docx',
]
"""Формат загрузки файлов для Литературы."""
