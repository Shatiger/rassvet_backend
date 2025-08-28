from django.contrib import admin

from content.base_models import BaseOrderedModelAdmin
from content.mixins import CharCountAdminMixin
from content.models.supervisors import Supervisor


@admin.register(Supervisor)
class SupervisorAdmin(CharCountAdminMixin, BaseOrderedModelAdmin):
    """Модель администрирования супервизоров."""

    charcount_fields = {
        'name': 19,
        'position': 70,
    }
    list_display = ('name', 'position', 'move_up_down_links')
    readonly_fields = ('created_at', 'updated_at')
    list_filter = (('directions', admin.RelatedOnlyFieldListFilter),)
    filter_horizontal = ('directions',)
