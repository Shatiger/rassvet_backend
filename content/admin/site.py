"""Кастомная админ-панель с группировкой моделей по разделам."""

from django.contrib.admin import AdminSite


class GroupedAdminSite(AdminSite):
    """Кастомная админ-панель с логической группировкой моделей."""

    site_header = 'Администрирование'
    site_title = 'Админ-панель'

    def get_app_list(self, request, app_label=None):
        """Формирует список разделов с моделями."""
        app_list = super().get_app_list(request, app_label)
        sections = {
            'Администраторы': ['RassvetUser', 'Group'],
            'О нас': ['AboutUsVideo', 'Review', 'Gratitude'],
            'Команда': [
                'Employee',
                'Supervisor',
            ],
            'Новости': ['News', 'Direction'],
            'База знаний': [
                'ChapterKnowledgeBase',
                'Article',
                'ChapterUsefulLinks',
                'Literature',
            ],
            'Помощь детям': [
                'TargetedFundraising',
            ],
            'Помощь родителям': [
                'Coaching',
            ],
            'Специалистам': [
                'TrainingAndInternships',
                'Vacancy',
            ],
            'Миссия': [
                'Mission',
            ],
            'Документы и отчеты': [
                'Chapter',
            ],
            'Партнеры и проекты': [
                'Partner',
                'ProgramsProjects',
                'Project',
            ],
        }
        all_models = {}
        for app in app_list:
            for model in app['models']:
                all_models[model['object_name']] = model
        new_app_list = []
        for section_name, model_names in sections.items():
            section_models = []
            for model_name in model_names:
                if model_name in all_models:
                    section_models.append(all_models[model_name])
            if section_models:
                new_app_list.append(
                    {
                        'name': section_name,
                        'app_label': section_name.lower().replace(' ', '_'),
                        'app_url': '#',
                        'has_module_perms': True,
                        'models': section_models,
                    }
                )
        return new_app_list


admin_site = GroupedAdminSite(name='myadmin')
