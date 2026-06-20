"""Модуль содержит модели, связанные с Консультациями и обучением.

Модели:
    1. Coaching: Модель для хранения Консультаций и обучения
    2. CoachingPhoto: Модель для хранения Фотографий Консультаций и обучения
    3. ButtonLink: Модель для хранения ссылок для кнопок перехода
"""

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from ordered_model.models import OrderedModel

from content.constants import CHAR_FIELD_LENGTH, IMAGE_CONTENT_TYPES
from content.mixins import TitleMixin


class Coaching(TitleMixin, OrderedModel):
    """Модель Консультаций и обучения."""

    class CourseFormatChoices(models.TextChoices):
        """Выбор формата курса."""

        ONLINE = 'online', 'онлайн'
        OFFLINE = 'offline', 'офлайн'
        HYBRID = 'hybrid', 'гибрид'

    class Buttons(models.TextChoices):
        """Выбор перехода на страницу."""

        ABA_THERAPY = 'aba_therapy', 'на страницу "АВА-терапия"'
        CONTACTS = 'contacts', 'на контакты'
        NEWS = 'news', 'ссылка на новость'

    photo = models.ImageField(
        upload_to='coaching/photos/',
        verbose_name='Фотография',
        validators=[FileExtensionValidator(IMAGE_CONTENT_TYPES)],
    )
    add_info = models.CharField(
        max_length=30,
        verbose_name='Дополнительная информация (на фото)',
        blank=True,
    )
    short_text = models.TextField(
        verbose_name='Краткое описание',
    )
    service_price = models.CharField(
        max_length=CHAR_FIELD_LENGTH,
        verbose_name='Цена услуги',
    )
    date = models.CharField(
        max_length=CHAR_FIELD_LENGTH,
        verbose_name='Дата или сроки проведения',
    )
    course_format = models.CharField(
        max_length=max(len(value) for value, _ in CourseFormatChoices.choices),
        choices=CourseFormatChoices.choices,
        verbose_name='Формат курса',
    )
    button = models.CharField(
        max_length=max(len(value) for value, _ in Buttons.choices),
        choices=Buttons.choices,
        default=Buttons.ABA_THERAPY,
        verbose_name='Тип перехода',
    )
    link_button = models.URLField(
        verbose_name='Ссылка на страницу новости',
        help_text='Ссылка вводится только для новости',
        blank=True,
    )

    class Meta(OrderedModel.Meta):
        """Класс Meta для Coaching, содержащий мета-данные."""

        indexes = [models.Index(fields=['order'])]
        verbose_name = 'Консультация и обучение'
        verbose_name_plural = 'Консультации и обучения'

    def clean(self):
        """Валидация поля link_button в зависмисти от выбора в поле button."""
        if self.button == 'news' and not self.link_button:
            raise ValidationError('Укажите ссылку на страницу новости.')
