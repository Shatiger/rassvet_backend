"""Модуль содержит модели, связанные с Консультациями и обучением.

Модели:
    1. Coaching: Модель для хранения Консультаций и обучения
    2. CoachingPhoto: Модель для хранения Фотографий Консультаций и обучения
    3. ButtonLink: Модель для хранения ссылок для кнопок перехода
"""

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone
from ordered_model.models import OrderedModel

from content.constants import CHAR_FIELD_LENGTH, IMAGE_CONTENT_TYPES
from content.mixins import TitleMixin


class Coaching(TitleMixin, OrderedModel):
    """Модель Консультаций и обучения."""

    class CourseFormatChoices(models.TextChoices):
        """Выбор формата курса."""

        ONLINE = 'online', 'онлайн'
        OFFLINE = 'offline', 'офлайн'

    class Buttons(models.TextChoices):
        """Выбор перехода на страницу."""

        ABA_THERAPY = 'aba_therapy', 'Узнать больше о АБА-терапия'
        CONTACTS = 'contacts', 'Позвонить'
        NEWS = 'news', 'Узнать больше о новости'

    short_text = models.TextField(
        verbose_name='Краткий текст',
    )
    service_price = models.CharField(
        max_length=CHAR_FIELD_LENGTH,
        verbose_name='цена услуги',
        help_text='внести текст и/или цифры',
    )
    date = models.DateField(
        verbose_name='Дата',
        default=timezone.now,
        db_index=True,
    )
    place = models.CharField(
        max_length=CHAR_FIELD_LENGTH,
        verbose_name='место',
        blank=True,
    )
    course_format = models.CharField(
        max_length=max(len(value) for value, _ in CourseFormatChoices.choices),
        choices=CourseFormatChoices.choices,
        verbose_name='формат курса',
    )
    button = models.CharField(
        max_length=max(len(value) for value, _ in Buttons.choices),
        choices=Buttons.choices,
        verbose_name='Кнопка',
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

    def __str__(self):
        """Возвращает строковое представление Coaching."""
        return self.title

    def clean(self):
        """Валидация поля link_button в зависмисти от выбора в поле button."""
        if self.button == 'news' and self.link_button is None:
            raise ValidationError('Укажите ссылку на страницу новости.')
        if self.button in ['aba_therapy', 'contacts'] and self.link_button:
            raise ValidationError(
                'Ссылка вводится только для кнопки "Узнать больше о новости".'
            )


class CoachingPhoto(models.Model):
    """Модель Фотографий Консультаций и обучения."""

    coaching = models.ForeignKey(
        Coaching,
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name='Консультации и обучение',
    )
    image = models.ImageField(
        upload_to='coaching/',
        verbose_name='Фотография',
        validators=[FileExtensionValidator(IMAGE_CONTENT_TYPES)],
    )

    class Meta:
        """Класс Meta для CoachingPhoto, содержащий мета-данные."""

        verbose_name = 'Фотография Консультаций и обучения'
        verbose_name_plural = 'Фотографии Консультаций и обучения'

    def __str__(self):
        """Возвращает строковое представление фотографии coaching."""
        return f'Фотография для coaching {self.coaching.title}'
