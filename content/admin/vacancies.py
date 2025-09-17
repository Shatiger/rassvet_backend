"""Модуль настройки административного интерфейса для вакансий."""

from django.contrib import admin

from content.base_models import TopOrderedModelAdmin

from content.mixins import CharCountAdminMixin
from content.models import Vacancy


@admin.register(Vacancy)
class VacancyAdmin(CharCountAdminMixin, TopOrderedModelAdmin):
    """Административная панель для управления вакансиями."""

    charcount_fields = {
        'profession': 70,
        'salary': 15,
        'schedule': 20,
        'short_description': 380,
    }
    list_display = [
        'profession',
        'salary',
        'schedule',
        'move_up_down_links',
    ]

    list_editable = [
        'salary',
    ]

    list_filter = [
        'profession',
    ]

    search_fields = [
        'profession',
    ]

    readonly_fields = [
        'created_at',
        'updated_at',
    ]

    fieldsets = (
        (
            'Основная информация карточки вакансии',
            {
                'fields': (
                    'profession',
                    'photo',
                    'short_description',
                    'salary',
                    'shedule',
                    'redirect_type',
                ),
                'description': 'Поля для карточки вакансии '
                'на странице "Специалистам"',
            },
        ),
        (
            'Информация для подробной страницы'
            '"Специалистам. Вакансия подробная"',
            {
                'fields': (
                    'additional_description',
                    'detailed_description',
                    'external_link',
                ),
                'description': 'Поля заполняемые при выборе '
                '"На страницу "Специалистам. Вакансия подробная". '
                'Если ссылка на внешнюю платформу не заполнена - '
                'кнопка перехода не появляется.',
            },
        ),
        (
            'Служебная информация',
            {'fields': ('created_at', 'updated_at'), 'classes': ['collapse']},
        ),
    )
