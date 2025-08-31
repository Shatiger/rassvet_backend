"""Модуль конфигурации для импорта данных в модели контентного приложения.

Словарь MODEL_CONFIG описывает правила импорта данных для следующих моделей:
- Direction (направления)
- Gratitude (благодарности)
- Review (отзывы)
- Partner (партнеры)
- TargetedFundraising (адресные сборы)
- Employee (сотрудники)

Для каждой модели указываются следующие параметры:
    - fields: словарь описания полей, где ключ — имя поля модели, а значение —
      словарь с опциями:
        - source (str, optional): имя поля в исходных данных.
        - default (Any, optional): значение по умолчанию.
        - transform (callable, optional): функция преобразования значения.
        - required (bool, optional): признак обязательности поля(Employee).
    - required_fields (list[str], optional): список обязательных колонок
      в исходных данных для успешной загрузки строки.

Этот конфиг используется в скриптах импорта для унификации логики
обработки и валидации данных перед их сохранением в базу данных.
"""

from content.models import (
    Direction,
    Employee,
    Gratitude,
    Partner,
    Project,
    ProjectsStatus,
    ProgramsProjects,
    Review,
)
from content.models.targeted_fundraisings import (
    FundraisingStatus,
    TargetedFundraising,
)

MODEL_CONFIG = {
    Gratitude: {
        'fields': {
            'title': {
                'source': 'title',
            },
            'order': {
                'source': 'order',
            },
            'is_active': {'default': True},
        },
        'required_fields': ['file'],
    },
    Direction: {
        'fields': {
            'name': {
                'source': 'name',
            },
            'slug': {
                'source': 'slug',
            },
        },
    },
    Review: {
        'fields': {
            'author_name': {
                'source': 'author_name',
            },
            'content': {
                'source': 'content',
            },
            'order': {
                'source': 'order',
            },
            'is_active': {
                'source': 'is_active',
                'default': True,
                'transform': lambda val, row, rn: str(val).lower()
                in ['1', 'true', 'да'],
            },
        },
    },
    Partner: {
        'fields': {
            'name': {
                'source': 'name',
                'default': lambda row, row_num: f'Партнёр #{row_num}',
            },
            'description': {'default': ''},
            'logo': {
                'source': 'logo',
            },
        },
        'required_fields': ['logo'],
    },
    TargetedFundraising: {
        'fields': {
            'title': {'source': 'title'},
            'short_description': {'source': 'short_description'},
            'fundraising_link': {'default': ''},
            'top_text_block': {'source': 'text1', 'default': ''},
            'center_text_block': {'source': 'text2', 'default': ''},
            'bottom_text_block': {'source': 'text3', 'default': ''},
            'status': {
                'source': 'status',
                'transform': lambda val, row, row_num: (
                    FundraisingStatus.ACTIVE
                    if str(val).lower() == 'актуальный'
                    else FundraisingStatus.COMPLETED
                ),
            },
            'order': {
                'source': 'order',
                'default': 0,
            },
        },
        'required_fields': ['title', 'short_description'],
    },
    Employee: {
        'fields': {
            'name': {
                'transform': lambda val, *_: val.strip(),
                'required': True,
            },
            'order': {
                'transform': lambda val, *_: (
                    int(val) if str(val).strip().isdigit() else 999
                ),
                'default': 999,
            },
            'main_specialities': {
                'source': 'main_specialities',
                'default': '',
            },
            'interviews': {'source': 'interviews', 'default': ''},
            'specialists_register': {
                'source': 'specialists_register',
                'default': '',
            },
            'category_on_main': {
                'source': 'category_on_main',
                'default': True,
            },
            'specialities': {'source': 'specialities', 'default': ''},
            'education': {'source': 'education', 'default': ''},
            'additional_education': {
                'source': 'additional_education',
                'default': '',
            },
            'trainings': {'source': 'trainings', 'default': ''},
        },
        'required_fields': ['name'],
    },
    Project: {
        'fields': {
            'title': {'source': 'title'},
            'status': {'default': ProjectsStatus.ACTIVE},
            'project_rassvet': {'default': True},
            'program': {
                'default': lambda val,
                r,
                r_num: ProgramsProjects.objects.get_or_create(
                    title='Основная программа'
                )[0],
            },
            'logo': {'default': 'projects/default.png'},
            'project_goal': {'default': ''},
            'project_tasks': {'default': ''},
            'project_description': {'default': ''},
            'achieved_results': {'default': ''},
        },
        'required_fields': ['title'],
    },
}


DIRECTION_MAP = {
    '1': 'Другие новости',
    '2': 'Досуг для детей с РАС',
    '3': 'Обучение специалистов',
    '4': 'АВА-терапия',
    '5': 'Информирование',
    '9': 'Помощь родителям',
    '12': 'Адаптивная физкультура',
    '13': 'СМИ о нас',
    '16': 'Жизнь «Рассвета»',
    '18': 'Дом синего слона',
    '19': 'Ресурсные классы',
    '22': 'Мы благодарим',
}
