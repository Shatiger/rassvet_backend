"""Административная конфигурация для отчётов и их вложенных элементов.

Этот модуль содержит:
- ChapterAdmin: конфигурация для модели Chapter.
- ReportInline: inline-класс для отчётов.
"""

from django.db.models import Count
from django.contrib import admin

from ordered_model.admin import (
    OrderedTabularInline,
    OrderedInlineModelAdminMixin,
)

from content.base_models import SafeOrderedModelAdmin
from content.mixins import SafeOrderedInlineModelAdminMixin
from content.models.report import Report, Chapter


class ReportInline(OrderedTabularInline):
    """Модель администрирования документов."""

    model = Report
    fields = ('title', 'file', 'download_icon', 'move_up_down_links', 'order')
    readonly_fields = ('move_up_down_links', 'order')
    ordering = ('order',)
    extra = 1


@admin.register(Chapter)
class ChapterAdmin(
    SafeOrderedInlineModelAdminMixin,
    OrderedInlineModelAdminMixin,
    SafeOrderedModelAdmin,
):
    """Модель администрирования разделов отчетов."""

    list_display = ('title', 'count', 'move_up_down_links')
    inlines = [ReportInline]
    search_fields = ('title',)
    list_prefetch_related = ['reports']

    def get_queryset(self, request):
        """Возвращает оптимизированный QuerySet для разделов отчётов."""
        qs = super().get_queryset(request)
        return qs.annotate(report_count=Count('reports'))

    @admin.display(description='Количество документов')
    def count(self, obj):
        """Возвращает количество отчётов, связанных с разделом."""
        return obj.report_count
