"""Административная конфигурация для Миссий и их вложенных элементов.

Этот модуль содержит:
- MissionAdmin: конфигурация для модели Mission.
"""

from django.contrib import admin
from django.shortcuts import redirect

from content.models.mission import Mission

from .site import admin_site


@admin.register(Mission, site=admin_site)
class MissionAdmin(admin.ModelAdmin):
    """Админ зона Миссий."""

    list_display = (
        'organization_mission',
        'ambitions',
        'goal_for_five_years',
        'tasks',
    )

    def has_add_permission(self, request):
        """Разрешает добавление нового объекта, если экземпляр не создан."""
        return not Mission.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """Запрещает удаление объекта Mission в админке."""
        return False

    def changelist_view(self, request, extra_context=None):
        """Перенаправляет на страницу изменения экземпляра Mission."""
        obj = Mission.get_solo()
        return redirect(f'./{obj.pk}/change/')
