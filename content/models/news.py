"""Модуль содержит модели направлений деятельности, новостей и галереи.

Модели:
    - Direction: Хранит направления деятельности
    - News: Содержит информацию о новостях
    - GalleryImage: Хранит изображения для подробных страниц новостей
"""

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone
from ordered_model.models import OrderedModel

from content.constants import IMAGE_CONTENT_TYPES
from content.mixins import (
    CleanEmptyHTMLMixin,
    TimestampMixin,
    TitleMixin,
)
from content.validators import validate_not_empty_html
from content.utils import ckeditor_function
from .projects import Project


def upload_file(instance, filename):
    """Генерирует путь к файлу для загрузки."""
    return f'news_gallery_images/{instance.news.id}/{filename}'


class Direction(TimestampMixin, models.Model):
    """Модель направления деятельности, к которому может относиться новость."""

    name = models.CharField('Название', max_length=100, unique=True)
    slug = models.SlugField('URL-слаг', max_length=100, unique=True)

    class Meta:
        """Мета-настройки модели Direction."""

        ordering = ['name']
        verbose_name = 'Направление деятельности'
        verbose_name_plural = 'Направления деятельности'

    def __str__(self):
        """Строковое представление направления."""
        return self.name


class News(TimestampMixin, TitleMixin, CleanEmptyHTMLMixin, models.Model):
    """Модель новости, содержащая информацию и детализированные поля."""

    class DetailPageChoices(models.TextChoices):
        """Выбор способа отображения подробной страницы новости."""

        CREATE = 'create', 'Создать подробную страницу'
        LINK = 'link', 'Прикрепить ссылку'
        NONE = 'none', 'Не создавать страницу'

    photo = models.ImageField(
        verbose_name='Фото',
        upload_to='news_photos/',
        validators=[FileExtensionValidator(IMAGE_CONTENT_TYPES)],
    )
    date = models.DateField('Дата новости', default=timezone.now)
    course_start = models.DateField('Старт курса', null=True, blank=True)
    summary = models.TextField(
        verbose_name='Краткий текст',
    )
    directions = models.ManyToManyField(
        Direction,
        verbose_name='Направление деятельности',
        related_name='news',
        related_query_name='news',
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Проект',
        related_name='news',
        related_query_name='news',
    )
    detail_page_type = models.CharField(
        'Подробная страница',
        max_length=10,
        choices=DetailPageChoices.choices,
        default=DetailPageChoices.NONE,
    )
    detail_page_link = models.URLField(
        'Ссылка на подробную страницу',
        blank=True,
    )
    show_on_main = models.BooleanField(
        'Отображение на странице Новости', default=True
    )
    full_text = ckeditor_function(
        verbose_name='Основной текст',
        blank=True,
        validators=[],
    )
    video_url = models.URLField(
        'Ссылка на видео',
        blank=True,
    )
    clean_html_fields = ('full_text', 'summary')

    class Meta:
        """Мета-настройки модели News."""

        ordering = ['-date']
        indexes = [
            models.Index(
                fields=['show_on_main', '-date'], name='news_main_date_idx'
            ),
            models.Index(
                fields=['project', '-date'], name='news_project_date_idx'
            ),
            models.Index(fields=['-date', 'id'], name='news_date_id_idx'),
        ]
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'

    def __str__(self):
        """Строковое представление направления."""
        return f'{self.title} ({self.date})'

    def save(self, *args, **kwargs):
        """Сохранение объекта с предварительной валидацией."""
        self.clean()
        super().save(*args, **kwargs)

    def clean(self):
        """Валидация полей в зависимости от типа подробной страницы."""
        if self.detail_page_type == 'create':
            validate_not_empty_html(
                self.full_text,
                'Для создания подробной страницы '
                'необходимо заполнить основной текст:.',
            )
        if self.detail_page_type == 'link' and not self.detail_page_link:
            raise ValidationError('Укажите ссылку на внешнюю страницу.')


class GalleryImage(TimestampMixin, OrderedModel):
    """Модель изображения в галерее новости."""

    news = models.ForeignKey(
        News,
        on_delete=models.CASCADE,
        related_name='gallery_images',
        verbose_name='Новость',
    )
    image = models.ImageField(
        verbose_name='Фото',
        upload_to=upload_file,
        validators=[FileExtensionValidator(IMAGE_CONTENT_TYPES)],
    )
    name = models.CharField('Название', max_length=100, default=image.name)
    order_with_respect_to = 'news'

    class Meta(OrderedModel.Meta):
        """Мета-настройки модели GalleryImage."""

        ordering = [
            'order',
        ]
        indexes = [
            models.Index(fields=['news', 'order']),
        ]
        verbose_name = 'Фотография'
        verbose_name_plural = 'Фотографии'

    def __str__(self):
        """Строковое представление для изображения."""
        return self.name
