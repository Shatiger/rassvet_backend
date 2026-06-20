"""Административная конфигурация для модели AboutUsVideo.

Этот модуль содержит класс AboutUsVideoAdmin, который управляет отображением
и поведением единственного экземпляра ссылки на видео в админке.
"""

from django.contrib import admin
from django.shortcuts import redirect

from content.models import AboutUsVideo

from .site import admin_site


@admin.register(AboutUsVideo, site=admin_site)
class AboutUsVideoAdmin(admin.ModelAdmin):
    """Отображение единственного экземпляра Video в админке.

    Класс обеспечивает:
    - редактирование только одного объекта;
    - отключение удаления;
    - автоматическое перенаправление на страницу редактирования
      единственного экземпляра.
    """

    list_display = ('video_orientation', 'url')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Основная информация', {'fields': ('video_orientation', 'url')}),
        (
            'Служебная информация',
            {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)},
        ),
    )

    def has_add_permission(self, request):
        """Разрешает добавление нового объекта, если экземпляр не создан."""
        return not AboutUsVideo.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """Запрещает удаление объекта AboutUsVideo в админке."""
        return False

    def changelist_view(self, request, extra_context=None):
        """Перенаправляет на страницу изменения экземпляра AboutUsVideo."""
        obj = AboutUsVideo.get_solo()
        return redirect(f'./{obj.pk}/change/')
