"""Модуль базовых классом для модэлей проекта.

Этот модуль содержит:
- TopOrderedModelAdmin: Класс для ordered моделей,
  добавляющий новую запись в начало.
- SafeOrderedModelAdmin: Базовый админ-класс, корректно обрабатывающий
  bulk-удаление ordered моделей.
"""
from django.db import transaction

from ordered_model.admin import OrderedModelAdmin


class SafeOrderedModelAdmin(OrderedModelAdmin):
    """Базовый админ-класс, обрабатывающий bulk-удаление ordered моделей."""

    def delete_queryset(self, request, queryset):
        """Массовое удаление через админку."""
        Model = queryset.model
        order_field = getattr(Model, 'order_field_name', 'order')
        group_fields = getattr(Model, 'order_with_respect_to', None)
        if isinstance(group_fields, str):
            group_fields = (group_fields,)
        with transaction.atomic():
            if group_fields:
                groups = queryset.values_list(*group_fields).distinct()
                for group_values in groups:
                    filter_ = dict(
                        zip(
                            group_fields,
                            group_values
                            if isinstance(group_values, tuple)
                            else (group_values,),
                        )
                    )
                    for obj in queryset.filter(**filter_).order_by(
                        f'-{order_field}'
                    ):
                        obj.delete()
            else:
                for obj in queryset.order_by(f'-{order_field}'):
                    obj.delete()


class TopOrderedModelAdmin(SafeOrderedModelAdmin):
    """Класс для ordered моделей, добавляющий новую запись в начало."""

    def save_model(self, request, obj, form, change):
        """Сохраняет объект модели в админке.

        При создании нового объекта автоматически перемещает его
        на верхнюю позицию (в начало списка), чтобы новые элементы
        отображались первыми. Для уже существующих объектов сохраняет
        стандартное поведение.
        """
        with transaction.atomic():
            super().save_model(request, obj, form, change)
            if change is False:
                obj.top()
