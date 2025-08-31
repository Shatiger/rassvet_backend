"""Модуль содержит модели относящиеся к обучению и стажировкам.

Модели:
    - FormatStudy: Перечисление фозможных форматов обученя
    - ActionOmButton: Перечисление действий при нажатии на кнопку
    - TrainingAndInternships: Содержит информацию об обучениях и стажировках
    - TrainingAndInternshipsPhoto: Хранит фотографии обучения и стажировок
"""

from django.core.validators import FileExtensionValidator
from django.db import models
from django.forms import ValidationError
from ordered_model.models import OrderedModel

from content.constants import IMAGE_CONTENT_TYPES
from content.mixins import CleanEmptyHTMLMixin, TitleMixin
from content.utils import ckeditor_function
from content.validators import validate_not_empty_html


class FormatStudy(models.TextChoices):
    """Формат учебы."""

    ONLINE = 'online', 'Онлайн'
    OFFLINE = 'offline', 'Оффлайн'
    HYBRID = 'hybrid', 'Гибридный'


class ActionOnButton(models.TextChoices):
    """Действие кнопки."""

    DETAIL = 'detail', 'Подробная страница'
    REGISTRATION = 'registration', 'Форма регистрации и отклика'
    URL_NEWS = 'url', 'Ссылка на новость'


class TrainingAndInternships(TitleMixin, CleanEmptyHTMLMixin, OrderedModel):
    """Модель обучения и стажировки."""

    add_info = models.CharField(
        max_length=25,
        verbose_name='Дополнительная информация',
        blank=True,
    )
    price = models.CharField(
        max_length=255,
        verbose_name='Цена',
        blank=True,
    )
    date = models.CharField(
        verbose_name='Дата',
        max_length=255,
    )
    format_study = models.CharField(
        max_length=max(len(value) for value, _ in FormatStudy.choices),
        choices=FormatStudy.choices,
        default=FormatStudy.ONLINE,
        verbose_name='Формат обучения',
    )
    location = models.CharField(
        max_length=255,
        verbose_name='Место проведения',
        blank=True,
    )
    short_description = models.TextField(verbose_name='Краткое описание')
    text_block = ckeditor_function(
        blank=True,
        verbose_name='Текстовый блок',
        validators=[],
    )
    action_on_button = models.CharField(
        max_length=max(len(value) for value, _ in ActionOnButton.choices),
        choices=ActionOnButton.choices,
        default=ActionOnButton.DETAIL,
        verbose_name='Действие на кнопке',
    )
    linked_news = models.URLField(
        verbose_name='Ссылка на новость',
        blank=True,
        max_length=200,
    )
    clean_html_fields = ('text_block',)

    class Meta(OrderedModel.Meta):
        """Класс Meta для TrainingAndInternships, содержащий мета-данные."""

        verbose_name = 'Обучение и стажировка'
        verbose_name_plural = 'Обучение и стажировки'
        ordering = ['order']

    def __str__(self):
        """Возвращает строковое представление обучения и стажировок."""
        return self.title

    def save(self, *args, **kwargs):
        """Сохранение объекта с предварительной валидацией."""
        self.clean()
        super().save(*args, **kwargs)

    def clean(self):
        """Валидация полей в зависимости от типа подробной страницы."""
        if self.action_on_button == ActionOnButton.DETAIL:
            validate_not_empty_html(
                self.text_block,
                'Для создания подробной страницы '
                'необходимо заполнить текстовый блок:.',
            )
        elif (
            self.action_on_button == ActionOnButton.URL_NEWS
            and not self.linked_news
        ):
            raise ValidationError('Ссылка на новость не может быть пустой')


class TrainingAndInternshipsPhoto(models.Model):
    """Модель Фотографий обучения и стажировок."""

    training = models.ForeignKey(
        TrainingAndInternships,
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name='Обучение и стажировка',
    )
    image = models.ImageField(
        upload_to='training/',
        verbose_name='Фотография',
        validators=[FileExtensionValidator(IMAGE_CONTENT_TYPES)],
    )
    on_main = models.BooleanField(
        default=False,
        verbose_name='На главной странице',
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Порядок отображения',
    )

    class Meta:
        """Класс Meta для TAIPhoto, содержащий мета-данные."""

        verbose_name = 'Фотография карточки обучения и стажировок'
        verbose_name_plural = 'Фотографии карточек обучения и стажировок'
        ordering = ['order']
        indexes = [models.Index(fields=['order'])]

    def __str__(self):
        """Возвращает строковое представление  фотографии."""
        return f'Фотография для карточки {self.training.title}'
