"""Модуль настройки административного интерфейса для новостей."""

from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from ordered_model.admin import (
    OrderedTabularInline,
    OrderedInlineModelAdminMixin,
)

from content.mixins import (
    CharCountAdminMixin,
    SafeOrderedInlineModelAdminMixin,
)
from content.models import News, Direction, GalleryImage, Project

from .site import admin_site


class ProjectFilterActive(SimpleListFilter):
    """Кастомный фильтр для проектов в административном интерфейсе новостей.

    Обеспечивает сортировку списка Действующих проектов по алфавиту в фильтре.
    """

    title = 'Действующий проект'
    parameter_name = 'active_project'

    def lookups(self, request, model_admin):
        """Возвращает список вариантов для фильтра."""
        projects = Project.objects.filter(status='active').order_by('title')
        return [(project.pk, project.title) for project in projects]

    def queryset(self, request, queryset):
        """Фильтрует queryset на основе выбранного значения."""
        if self.value():
            return queryset.filter(project=self.value())
        return queryset


class ProjectFilterCompleted(SimpleListFilter):
    """Кастомный фильтр для проектов в административном интерфейсе новостей.

    Обеспечивает сортировку списка Завершенных проектов по алфавиту в фильтре.
    """

    title = 'Завершенный проект'
    parameter_name = 'completed_project'

    def lookups(self, request, model_admin):
        """Возвращает список вариантов для фильтра."""
        projects = Project.objects.filter(status='completed').order_by('title')
        return [(project.pk, project.title) for project in projects]

    def queryset(self, request, queryset):
        """Фильтрует queryset на основе выбранного значения."""
        if self.value():
            return queryset.filter(project=self.value())
        return queryset


class GalleryImageInline(OrderedTabularInline):
    """Инлайн для изображений галереи новости (до 15 штук)."""

    model = GalleryImage
    fields = (
        'image',
        'name',
        'move_up_down_links',
    )
    readonly_fields = ('move_up_down_links',)
    ordering = ('order',)
    extra = 1
    max_num = 15


@admin.register(News, site=admin_site)
class NewsAdmin(
    CharCountAdminMixin,
    SafeOrderedInlineModelAdminMixin,
    OrderedInlineModelAdminMixin,
    admin.ModelAdmin,
):
    """Настройка административного интерфейса для модели News."""

    charcount_fields = {
        'title': 100,
        'summary': 280,
    }
    inlines = [GalleryImageInline]
    list_display = ('__str__', 'date', 'show_on_main', 'project')
    list_editable = ('date', 'show_on_main')
    list_filter = (
        'date',
        'show_on_main',
        ProjectFilterActive,
        ProjectFilterCompleted,
        'directions',
        'detail_page_type',
    )
    search_fields = ('title', 'summary', 'full_text')
    filter_horizontal = ('directions',)
    list_select_related = ('project',)
    list_per_page = 25
    fieldsets = (
        (
            'Основная информация карточки новости',
            {
                'fields': (
                    'date',
                    'title',
                    'photo',
                    'course_start',
                    'summary',
                    'directions',
                    'project',
                )
            },
        ),
        (
            'Детализация',
            {
                'fields': (
                    'detail_page_type',
                    'detail_page_link',
                    'show_on_main',
                )
            },
        ),
        (
            'Контент подробной страницы',
            {'fields': ('full_text', 'video_url', 'video_orientation')},
        ),
    )


@admin.register(Direction, site=admin_site)
class DirectionAdmin(admin.ModelAdmin):
    """Настройка административного интерфейса для модели Direction."""

    list_display = ('__str__', 'slug')
    search_fields = ('name',)
