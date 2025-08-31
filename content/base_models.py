"""Модуль базовых классом для модэлей проекта.

Этот модуль содержит:
- BaseOrderedModelAdmin: Базовый класс для OrderedModelAdmin.
"""

from ordered_model.admin import OrderedModelAdmin


class BaseOrderedModelAdmin(OrderedModelAdmin):
    """Базовый класс для OrderedModelAdmin."""

    def save_model(self, request, obj, form, change):
        """Сохраняет объект модели в админке.

        При создании нового объекта автоматически перемещает его
        на верхнюю позицию (в начало списка), чтобы новые элементы
        отображались первыми. Для уже существующих объектов сохраняет
        стандартное поведение.
        """
        super().save_model(request, obj, form, change)
        if change is False:
            obj.top()
