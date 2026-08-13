"""Пакет моделей приложения content.

Содержит все модели данных, используемые для управления контентом:
- Благодарности
- Отзывы
- Партнёры
- Видео "О нас"
- Адресные сборы и связанные сущности
- Сотрудники и их документы
- Проекты
- Новости
- Литература
- Поисковый индекс

Все модели регистрируются здесь для обеспечения корректного импорта и миграций.
"""

from .about_us_video import AboutUsVideo
from .coaching import Coaching
from .employees import Document, Employee, TypeDocument
from .gratitudes import Gratitude
from .knowledge_base import (
    Article,
    ArticleGallery,
    ArticleTextBlock,
    ArticleVideoLink,
    ChapterKnowledgeBase,
)
from .literatures import Literature
from .mission import Mission
from .news import Direction, GalleryImage, News
from .partners import Partner
from .projects import ProgramsProjects, Project, ProjectPhoto, ProjectsStatus
from .reviews import Review
from .search import SearchEntityType, SearchEntry
from .supervisors import Supervisor
from .targeted_fundraisings import (
    FundraisingPhoto,
    TargetedFundraising,
)
from .useful_links import ArticleUsefulLinks, ChapterUsefulLinks
from .report import Report, Chapter
from .vacancies import Vacancy
from .training_and_internships import (
    FormatStudy,
    ActionOnButton,
    TrainingAndInternships,
    TrainingAndInternshipsPhoto,
)

__all__ = [
    'AboutUsVideo',
    'Article',
    'ArticleGallery',
    'ArticleTextBlock',
    'ArticleVideoLink',
    'ArticleUsefulLinks',
    'ChapterKnowledgeBase',
    'ChapterUsefulLinks',
    'Coaching',
    'Chapter',
    'Direction',
    'Document',
    'Employee',
    'FundraisingPhoto',
    'GalleryImage',
    'Gratitude',
    'Literature',
    'Mission',
    'News',
    'Partner',
    'ProgramsProjects',
    'Project',
    'ProjectPhoto',
    'ProjectsStatus',
    'Report',
    'Review',
    'SearchEntityType',
    'SearchEntry',
    'Supervisor',
    'TargetedFundraising',
    'TypeDocument',
    'Vacancy',
    'FormatStudy',
    'ActionOnButton',
    'TrainingAndInternships',
    'TrainingAndInternshipsPhoto',
]
