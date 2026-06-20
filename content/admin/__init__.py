"""Пакет админских классов для приложения content."""
from . import training_and_internships
from . import vacancies
from . import useful_links
from . import targeted_fundraisings
from . import supervisors
from . import reviews
from . import report
from . import projects
from . import partners
from . import news
from . import literatures
from . import mission
from . import knowledge_base
from . import gratitudes
from . import employees
from . import coaching
from . import about_us_video
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin

from .site import admin_site

admin_site.register(Group, GroupAdmin)


__all__ = [
    'training_and_internships',
    'vacancies',
    'useful_links',
    'targeted_fundraisings',
    'supervisors',
    'reviews',
    'report',
    'projects',
    'partners',
    'news',
    'literatures',
    'mission',
    'knowledge_base',
    'gratitudes',
    'employees',
    'coaching',
    'about_us_video',
]
