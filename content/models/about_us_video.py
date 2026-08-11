"""Модуль about_us_video содержит модель для данных о видео в разделе 'О нас'.

Модели:
    AboutUsVideo: Модель для хранения заголовка и URL ссылки на видео, а также
                  даты создания и обновления.
"""

from django.db import models
from django.core.validators import RegexValidator

from content.constants import EMPTY_VALUE_DISPLAY
from content.mixins import TimestampMixin, VideoOrientationMixin


class AboutUsVideo(VideoOrientationMixin, TimestampMixin, models.Model):
    """Модель для хранения информации о видео в разделе 'О нас'."""

    video_orientation = models.CharField(
        max_length=VideoOrientationMixin.video_orientation_max_length(),
        choices=VideoOrientationMixin.VideoOrientationChoices.choices,
        default=VideoOrientationMixin.VideoOrientationChoices.HORIZONTAL,
        verbose_name='Ориентация видео',
    )
    url = models.CharField(
        verbose_name = 'Ссылка на видео',
        blank=True,
        max_length=500,
        validators=[
            RegexValidator(
                regex=r'^(https?://|/).*$',
                message='Введите корректный URL или относительный путь (начинается с /)',
            )
        ]
    )

    class Meta:
        """Класс Meta, который содержит мета-данные для модели."""

        verbose_name = 'Видео о нас'
        verbose_name_plural = 'Видео о нас'

    def __str__(self):
        """Возвращает строковое представление объекта видео."""
        return 'Видео о нас' or EMPTY_VALUE_DISPLAY

    @classmethod
    def get_solo(cls):
        """Получает единственное видео для раздела 'О нас'.

        Если видео не существует, будет создано одно видео.
        """
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
