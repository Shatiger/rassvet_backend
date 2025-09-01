"""Модуль настройки административного интерфейса для вакансий."""

from django.contrib import admin

from content.base_models import TopOrderedModelAdmin

from content.models import Vacancy


@admin.register(Vacancy)
class VacancyAdmin(TopOrderedModelAdmin):
    """Административная панель для управления вакансиями."""

    list_display = [
        'profession',
        'salary',
        'schedule',
        'location',
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
        'short_description',
        'location',
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
                    'salary',
                    'short_description',
                    'redirect_type',
                ),
                'description': 'Обязательные поля для карточки вакансии '
                'на странице "Вакансии"',
            },
        ),
        (
            'Дополнительная информация карточки',
            {
                'fields': ('schedule', 'location'),
                'description': 'Необязательные поля для карточки вакансии',
            },
        ),
        (
            'Информация для подробной страницы "Вакансии_подробная"',
            {
                'fields': (
                    'additional_description',
                    'detailed_description',
                    'external_link',
                ),
                'description': 'Поля заполняемые при выборе '
                '"На страницу Вакансии_подробная". '
                'Если ссылка на внешнюю платформу не заполнена - '
                'кнопка перехода на НН не появляется.',
            },
        ),
        (
            'Служебная информация',
            {'fields': ('created_at', 'updated_at'), 'classes': ['collapse']},
        ),
    )
