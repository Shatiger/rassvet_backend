"""Модуль для импорта данных о видео "О нас" в базу данных."""

import csv
import os

from django.core.management.base import BaseCommand

from content.models import AboutUsVideo

DATA_PATH = 'data/'


class Command(BaseCommand):
    """Команда Django для импорта видео "О нас"."""

    help = 'Импорт данных о видео из TXT-файла в базу данных'

    def handle(self, *args, **kwargs):
        """Запускает процесс импорта данных."""
        self.stdout.write("Начинаем импорт видео 'О нас'...")
        with open(
            os.path.join(DATA_PATH, 'video.txt'), 'r', encoding='utf-8'
        ) as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                AboutUsVideo.objects.update_or_create(
                    url=row['url'],
                )
        self.stdout.write(self.style.SUCCESS("Импорт видео 'О нас' завершен."))
