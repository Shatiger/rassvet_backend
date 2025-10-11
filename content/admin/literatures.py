from django.contrib import admin

from content.base_models import TopOrderedModelAdmin
from content.models import Literature

from .site import admin_site


@admin.register(Literature, site=admin_site)
class LiteratureAdmin(TopOrderedModelAdmin):
    """Модель администрирования литературы."""

    list_display = (
        'title',
        'author',
        'publication_year',
        'move_up_down_links',
    )
    search_fields = ('title', 'author')
