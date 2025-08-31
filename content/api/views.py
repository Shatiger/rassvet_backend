"""Представления для API приложения content.

Содержит представления для следующих моделей:
- Gratitude (благодарности)
- Mission (миссии)
- Partner (партнеры)
- Project (проекты)
- Review (отзывы)
- AboutUsVideo (видео о нас)
- TargetedFundraising (адресные сборы)
- Employee (сотрудники)

Используются только для чтения (GET-запросов).
"""

from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from content import filters
from content.mixins import MultiSerializerViewSetMixin
from content.models import (
    AboutUsVideo,
    Article,
    Chapter,
    ChapterKnowledgeBase,
    ChapterUsefulLinks,
    Coaching,
    Direction,
    Employee,
    Gratitude,
    Literature,
    Mission,
    News,
    Partner,
    Project,
    Review,
    Supervisor,
    TargetedFundraising,
    Vacancy,
    TrainingAndInternships,
)
from content.models.employees import Document
from content.models.news import GalleryImage
from content.models.report import Report
from content.pagination import (
    LiteraturePageNumberPagination,
    NewsLimitOffsetPagination,
)

from . import serializers


@extend_schema(tags=['Gratitudes group'])
@extend_schema_view(
    list=extend_schema(
        summary='Получить список Благодарностей.',
    ),
    retrieve=extend_schema(
        summary='Получить Благодарность по ID.',
    ),
)
class GratitudeViewSet(viewsets.ReadOnlyModelViewSet):
    """Получение благодарностей.

    Используйте этот эндпоинт, чтобы отобразить благодарности.
    Можно получить как весь список, так и одну благодарность по ID.
    """

    queryset = Gratitude.objects.filter(is_active=True)
    serializer_class = serializers.GratitudeSerializer


@extend_schema(tags=['Partners group'])
@extend_schema_view(
    list=extend_schema(
        summary='Получить список карточек Партнеров.',
    ),
    retrieve=extend_schema(
        summary='Получить карточку Партнера по ID.',
    ),
)
class PartnersViewSet(viewsets.ReadOnlyModelViewSet):
    """Информация о партнёрах.

    Используйте этот эндпоинт, чтобы отобразить информацию о партнёрах.
    Можно получить как весь список, так и одного партнёра по ID.
    """

    queryset = Partner.objects.all()
    serializer_class = serializers.PartnersSerializer


@extend_schema(tags=['Reviews group'])
@extend_schema_view(
    list=extend_schema(
        summary='Получить список Отзывов.',
    ),
    retrieve=extend_schema(
        summary='Получить Отзыв по ID.',
    ),
)
class ReviewViewSet(viewsets.ReadOnlyModelViewSet):
    """Информация об отзывах.

    Используйте этот эндпоинт, чтобы отобразить информацию об отзывах.
    Можно получить как весь список, так и один отзыв по ID.
    """

    queryset = Review.objects.filter(is_active=True)
    serializer_class = serializers.ReviewSerializer


@extend_schema(tags=['VideoAboutUs group'])
@extend_schema_view(
    list=extend_schema(
        summary='Получить Видео.',
    )
)
class AboutUsVideoViewSet(viewsets.GenericViewSet):
    """Информация о видео об организации.

    Возвращает одно видео с названием и ссылкой на источник.
    Используется для блока "О нас".
    """

    serializer_class = serializers.AboutUsVideoSerializer

    def list(self, request, *args, **kwargs):
        """Возвращает единственное видео для блока 'О нас'.

        Если видео не найдено, возвращает 404.
        """
        video = AboutUsVideo.get_solo()
        if not video:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(video)
        return Response(serializer.data)


@extend_schema(tags=['Fundraisings group'])
@extend_schema_view(
    list=extend_schema(
        summary='Получить список Адресных сборов.',
        description="""
        Получить список Адресных сборов с достаточной информацией о сборе.
        """,
    ),
    retrieve=extend_schema(
        summary='Получить Адресный сбор по ID.',
        description="""
        Получить Адресный сбор по ID с полной информацией о сборе.
        """,
    ),
)
class TargetedFundraisingViewSet(
    MultiSerializerViewSetMixin, viewsets.ReadOnlyModelViewSet
):
    """Информация об адресных сборах.

    Используйте этот эндпоинт, чтобы отобразить информацию об адресных сборах.
    Можно получить как весь список, так и один адресный сбор по ID.
    """

    serializer_classes = {
        'list': serializers.TargetedFundraisingListSerializer,
        'retrieve': serializers.TargetedFundraisingDetailSerializer,
    }

    def get_queryset(self):
        """Возвращает оптимизированный queryset."""
        if self.action == 'retrieve':
            return TargetedFundraising.objects.prefetch_related(
                'photos',
            )

        return TargetedFundraising.objects.prefetch_related('photos')


@extend_schema(tags=['Employees group'])
@extend_schema_view(
    list=extend_schema(
        summary='Получить список Сотрудников.',
    ),
    retrieve=extend_schema(
        summary='Получить карточку Сотрудника по ID.',
    ),
)
class EmployeeViewSet(
    MultiSerializerViewSetMixin, viewsets.ReadOnlyModelViewSet
):
    """Информация о сотрудниках.

    Используйте этот эндпоинт, чтобы отобразить информацию о сотрудниках.
    Можно получить как весь список, так и одного сотрудника по ID.
    """

    serializer_classes = {
        'list': serializers.EmployeeSerializer,
        'retrieve': serializers.EmployeeDetailSerializer,
    }

    def get_queryset(self):
        """Оптимизирует выборку данных для разных типов запросов.

        - Для retrieve использует prefetch_related для вложенных данных.
        - Для list возвращает базовый queryset сотрудников.
        """
        if self.action == 'retrieve':
            return Employee.objects.prefetch_related(
                Prefetch(
                    'documents',
                    queryset=Document.objects.select_related('type'),
                    to_attr='prefetched_documents',
                ),
                Prefetch(
                    'documents',
                    queryset=Document.objects.filter(
                        on_main_page=True
                    ).select_related('type'),
                    to_attr='prefetched_documents_on_main',
                ),
            )
        return Employee.objects.all()


@extend_schema(tags=['Projects group'])
@extend_schema_view(
    list=extend_schema(
        summary='Получить список Проектов.',
    ),
    retrieve=extend_schema(
        summary='Получить Проект по ID.',
    ),
)
class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    """Получить список Проектов, или конкретный по его ID."""

    queryset = (
        Project.objects.select_related('source_financing', 'program')
        .prefetch_related('photos')
        .all()
    )
    serializer_class = serializers.ProjectSerializer


@extend_schema(tags=['Missions group'])
@extend_schema_view(
    list=extend_schema(
        summary='Получить Миссию.',
    ),
)
class MissionViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """Получить Миссию."""

    serializer_class = serializers.MissionSerializer

    def list(self, request, *args, **kwargs):
        """Возвращает единственную Миссию'.

        Если Миссия не найдена, возвращает 404.
        """
        mission = Mission.get_solo()
        if not mission:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(mission)
        return Response(serializer.data)


@extend_schema(tags=['News group'])
@extend_schema_view(
    list=extend_schema(
        summary='Получить список Новостей.',
    ),
    retrieve=extend_schema(
        summary='Получить Новость по ID.',
    ),
)
class NewsViewSet(MultiSerializerViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """Получить список Новостей, или конкретную по её ID."""

    queryset = News.objects.select_related('project').prefetch_related(
        'directions',
        Prefetch(
            'gallery_images', queryset=GalleryImage.objects.order_by('order')
        ),
    )
    filter_backends = [DjangoFilterBackend]
    filterset_class = filters.NewsFilter
    pagination_class = NewsLimitOffsetPagination
    serializer_classes = {
        'list': serializers.NewsSerializer,
        'retrieve': serializers.NewsDetailSerializer,
    }


@extend_schema(tags=['Directions group'])
@extend_schema_view(
    list=extend_schema(
        summary='Получить список Направлений.',
    ),
    retrieve=extend_schema(
        summary='Получить Направление по ID.',
    ),
)
class DirectionViewSet(viewsets.ReadOnlyModelViewSet):
    """Получить список Направлений, или конкретное по его ID."""

    queryset = Direction.objects.all()
    serializer_class = serializers.DirectionSerializer


@extend_schema(tags=['Reports group'])
@extend_schema_view(
    list=extend_schema(
        summary='Получить список отчетов.',
        description="""
        Получить список отчетов с сортировкой по разделам.
        """,
    ),
    retrieve=extend_schema(
        summary='Получить список отчетов раздела.',
        description="""
        Получить список отчетов одного раздела.
        """,
    ),
)
class ReportViewSet(viewsets.ReadOnlyModelViewSet):
    """Получить список отчетов, или конкретный по его ID."""

    queryset = Chapter.objects.prefetch_related(
        Prefetch(
            'reports',
            queryset=Report.objects.select_related(),
        )
    ).all()
    serializer_class = serializers.ChapterSerializer


@extend_schema(tags=['Coachings group'])
@extend_schema_view(
    list=extend_schema(
        summary='Получить список "Консультация и обучение".',
    ),
    retrieve=extend_schema(
        summary='Получить "Консультация и обучение" по ID.',
    ),
)
class CoachingViewSet(viewsets.ReadOnlyModelViewSet):
    """Получить список "Консультация и обучение", или конкретный по его ID."""

    queryset = Coaching.objects.prefetch_related(
        'photos',
    ).all()
    serializer_class = serializers.CoachingSerializer


@extend_schema(tags=['Vacancies group'])
@extend_schema_view(
    list=extend_schema(
        summary='Получить список Вакансий.',
    ),
    retrieve=extend_schema(
        summary='Получить Вакансию по ID.',
    ),
)
class VacancyViewSet(
    MultiSerializerViewSetMixin, viewsets.ReadOnlyModelViewSet
):
    """Получить список Вакансий, или конкретную по её ID."""

    queryset = Vacancy.objects.all()
    serializer_classes = {
        'list': serializers.VacancySerializer,
        'retrieve': serializers.VacancyDetailSerializer,
    }


@extend_schema(tags=['Supervisors group'])
@extend_schema_view(
    list=extend_schema(
        summary='Получить список Супервизоров.',
    ),
    retrieve=extend_schema(
        summary='Получить Супервизора по ID.',
    ),
)
class SupervisorViewSet(viewsets.ReadOnlyModelViewSet):
    """Получить список Супервизоров, или конкретного по его ID."""

    queryset = Supervisor.objects.only(
        'id', 'name', 'position', 'image', 'order'
    ).prefetch_related(
        Prefetch(
            'directions', queryset=Direction.objects.only('id', 'name', 'slug')
        )
    )
    serializer_class = serializers.SupervisorSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.SupervisorFilter

    def get_queryset(self):
        """Возвращает QuerySet с устранением дубликатов при фильтрации."""
        queryset = super().get_queryset()
        if self.request is not None and (
            self.request.GET.get('direction_slugs')
        ):
            queryset = queryset.distinct()
        return queryset


@extend_schema(tags=['KnowledgeBase group'])
@extend_schema_view(
    list=extend_schema(
        summary='Получить список "Разделов Базы знаний".',
    ),
    retrieve=extend_schema(
        summary='Получить "Раздел Базы знаний" по ID.',
    ),
)
class ChapterKnowledgeBaseViewSet(viewsets.ReadOnlyModelViewSet):
    """Получить список "Разделов Базы знаний", или конкретный по его ID."""

    queryset = ChapterKnowledgeBase.objects.prefetch_related(
        'articles',
        'articles__gallery_photos',
        'articles__text_blocks',
    ).all()
    serializer_class = serializers.ChapterKnowledgeBaseSerializer


@extend_schema(tags=['KnowledgeBase group'])
@extend_schema_view(
    list=extend_schema(
        summary='Получить список "Статьи Базы знаний".',
    ),
    retrieve=extend_schema(
        summary='Получить "Статью Базы знаний" по ID.',
    ),
)
class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """Получить список "Разделов Базы знаний", или конкретный по его ID."""

    queryset = (
        Article.objects.select_related('chapter')
        .prefetch_related(
            'gallery_photos',
            'text_blocks',
        )
        .all()
    )
    serializer_class = serializers.ArticleSerializer


@extend_schema(tags=['UsefulLinks group'])
@extend_schema_view(
    list=extend_schema(
        summary='Получить список Разделов Полезные ссылки.',
    ),
    retrieve=extend_schema(
        summary='Получить Раздел Полезные ссылки по ID.',
    ),
)
class ChapterUsefulLinksViewSet(viewsets.ReadOnlyModelViewSet):
    """Получить список Разделов Полезные ссылки, или конкретный по его ID."""

    queryset = ChapterUsefulLinks.objects.prefetch_related(
        'article_useful_links',
    ).all()
    serializer_class = serializers.ChapterUsefulLinksSerializer


@extend_schema(tags=['Literature group'])
@extend_schema_view(
    list=extend_schema(
        summary='Получить список Литературы.',
    ),
    retrieve=extend_schema(
        summary='Получить Литературу по ID.',
    ),
)
class LiteratureViewSet(viewsets.ReadOnlyModelViewSet):
    """Получить список Литературы, или конкретную по ID."""

    queryset = Literature.objects.all()
    pagination_class = LiteraturePageNumberPagination
    serializer_class = serializers.LiteratureSerializer


@extend_schema(tags=['Training and internships'])
@extend_schema_view(
    list=extend_schema(
        summary='Получить список обучений и стажировок.',
    ),
    retrieve=extend_schema(
        summary='Получить подробно об обучению или стажировке.',
    ),
)
class TrainingAndInternshipsViewSet(
    MultiSerializerViewSetMixin, viewsets.ReadOnlyModelViewSet
):
    """Получить список Обучений и Стажировок, или конкретную по её ID."""

    queryset = TrainingAndInternships.objects.prefetch_related('photos')
    serializer_classes = {
        'list': serializers.TrainAndInternSerializer,
        'retrieve': serializers.TrainAndInternDetailSerializer,
    }
