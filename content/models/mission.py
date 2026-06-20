"""Модуль содержит модели, связанные с Миссиями.

Модели:
    1. Mission: Модель для хранения информации о Миссии
"""

from django.db import models
from django.utils.html import strip_tags

from content.utils import ckeditor_function


class Mission(models.Model):
    """Модель Миссии."""

    organization_mission = ckeditor_function('Миссия организации')
    ambitions = ckeditor_function('Амбиции')
    goal_for_five_years = ckeditor_function('Цель на 5 пять лет')
    tasks = ckeditor_function('Задачи')

    class Meta:
        """Класс Meta для Mission, содержащий мета-данные."""

        verbose_name = 'Миссия'
        verbose_name_plural = 'Миссии'

    def __str__(self):
        """Возвращает строковое представление Миссии организации."""
        title = strip_tags(self.organization_mission)
        if len(title) > 100:
            return f'{title[:100]}...'
        return title

    @classmethod
    def get_solo(cls):
        """Получает единственную Миссию'.

        Если Миссия не существует, будет создана одна Миссия.
        """
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
