from django.contrib import admin

from content.base_models import TopOrderedModelAdmin
from content.mixins import CharCountAdminMixin
from content.models.supervisors import Supervisor

from .site import admin_site


@admin.register(Supervisor, site=admin_site)
class SupervisorAdmin(CharCountAdminMixin, TopOrderedModelAdmin):
    """Модель администрирования супервизоров."""

    charcount_fields = {
        'name': 19,
        'position': 70,
    }
    list_display = (
        '__str__',
        'position',
        'move_up_down_links',
    )
    readonly_fields = ('created_at', 'updated_at')
    list_filter = (('directions', admin.RelatedOnlyFieldListFilter),)
    filter_horizontal = ('directions',)
