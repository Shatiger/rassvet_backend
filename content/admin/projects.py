"""Административная конфигурация для проектов и их вложенных элементов.

Этот модуль содержит:
- ProgramsProjectsAdmin: конфигурация для модели ProgramsProjects.
- ProjectPhotoAdmin: inline-класс для фотографий проекта.
- ProjectAdmin: конфигурация для модели Project.
"""

from django.contrib import admin
from django.utils.html import format_html

from content.base_models import TopOrderedModelAdmin
from content.mixins import CharCountAdminMixin
from content.models.projects import ProgramsProjects, Project, ProjectPhoto

from .site import admin_site


@admin.register(ProgramsProjects, site=admin_site)
class ProgramsProjectsAdmin(admin.ModelAdmin):
    """Админ зона Программ."""

    list_display = ('title',)
    search_fields = ('title',)

    def has_delete_permission(self, request, obj=None):
        """Запрещает удаление объекта ProgramsProjects в админке."""
        return False


class ProjectPhotoAdmin(admin.StackedInline):
    """Inline-класс для фотографий, прикреплённых к проекту."""

    model = ProjectPhoto
    min_num = 1
    max_num = 3


@admin.register(Project, site=admin_site)
class ProjectAdmin(CharCountAdminMixin, TopOrderedModelAdmin):
    """Админ зона Проектов."""

    charcount_fields = {
        'title': 100,
    }
    list_display = (
        'title',
        'program',
        'status',
        'logo_preview',
        'move_up_down_links',
    )
    list_editable = ('status',)
    list_filter = (
        'status',
        'program',
    )
    search_fields = (
        'title',
        'status',
    )
    inlines = (ProjectPhotoAdmin,)
    empty_value_display = '-пусто-'
    list_select_related = ('program', 'source_financing')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Сортирует выпадающие списки в формах."""
        if db_field.name in ('source_financing',):
            kwargs['queryset'] = db_field.related_model.objects.order_by(
                'name'
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    @admin.display(description='Логотип')
    def logo_preview(self, obj):
        """Отображает превью логотипа."""
        if obj.logo:
            return format_html('<img src="{}" width="50" />', obj.logo.url)
        return '—'
