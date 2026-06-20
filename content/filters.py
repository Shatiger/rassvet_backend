"""Модуль фильтров для API."""

import django_filters

from rest_framework.exceptions import ValidationError
from django.utils import timezone

from .constants import MAX_NEWS_YEAR_OFFSET, MIN_NEWS_REASONABLE_YEAR
from .models import Supervisor, News


def get_max_year():
    """Возвращает максимальное значение года для фильтрации."""
    return timezone.now().year + MAX_NEWS_YEAR_OFFSET


class NewsFilter(django_filters.FilterSet):
    """Фильтр новостей по диапазону годов и направлениям деятельности."""

    direction_slugs = django_filters.BaseInFilter(
        field_name='directions__slug', lookup_expr='in'
    )

    year_from = django_filters.NumberFilter(
        field_name='date',
        lookup_expr='year__gte',
        method='filter_year_from',
    )

    year_to = django_filters.NumberFilter(
        field_name='date',
        lookup_expr='year__lte',
        method='filter_year_to',
    )

    class Meta:
        """Метаданные фильтра: настраивает модель и поля фильтрации."""

        model = News
        fields = ('year_from', 'year_to', 'project', 'direction_slugs')

    def filter_year_from(self, queryset, name, value):
        """Фильтрует новости по минимальному году с валидацией диапазона."""
        if value is not None:
            if not (MIN_NEWS_REASONABLE_YEAR <= value <= get_max_year()):
                raise ValidationError(
                    {
                        'year_from': 'Год должен быть в диапазоне '
                        f'{MIN_NEWS_REASONABLE_YEAR}-{get_max_year()}'
                    }
                )
            return queryset.filter(date__year__gte=value)
        return queryset

    def filter_year_to(self, queryset, name, value):
        """Фильтрует новости по максимальному году с валидацией диапазона."""
        if value is not None:
            if not (MIN_NEWS_REASONABLE_YEAR <= value <= get_max_year()):
                raise ValidationError(
                    {
                        'year_to': 'Год должен быть в диапазоне '
                        f'{MIN_NEWS_REASONABLE_YEAR}-{get_max_year()}'
                    }
                )
            return queryset.filter(date__year__lte=value)
        return queryset


class SupervisorFilter(django_filters.FilterSet):
    """Фильтр супервизоров по направлениям деятельности."""

    direction_slugs = django_filters.BaseInFilter(
        field_name='directions__slug', lookup_expr='in'
    )

    class Meta:
        """Метаданные фильтра: настраивает модель и поля фильтрации."""

        model = Supervisor
        fields = ('direction_slugs',)
