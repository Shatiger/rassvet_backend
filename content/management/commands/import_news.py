"""Django management команда для импорта новостей из дампа SQL."""

import os
import re
import requests
from typing import List, Dict, Optional

from django.core.management.base import BaseCommand
from django.core.files import File
from django.core.files.base import ContentFile
from django.utils.dateparse import parse_date

from content.management.config import DIRECTION_MAP
from content.models import Direction, News, Project, GalleryImage

SKIP_DIRECTIONS = ('10', '17', '20')
EXPECTED_FIELDS = {'news': 15, 'projects': 4}


class SQLParser:
    """Парсер SQL дампа."""

    @staticmethod
    def safe_str(value) -> str:
        """Очищает строковое значение."""
        value = str(value).strip()
        if value == "''" or value.lower() in ('none', 'nan'):
            return ''
        if value.startswith("'") and value.endswith("'"):
            value = value[1:-1]
        return (
            value.replace("\\'", "'").replace('\\"', '"').replace('\\\\', '\\')
        )

    @staticmethod
    def safe_date(value):
        """Конвертирует строку в дату."""
        value = SQLParser.safe_str(value)
        try:
            return parse_date(value[:10])
        except Exception:
            return None

    @staticmethod
    def clean_text(value) -> str:
        """Очищает текст от переносов."""
        return (
            value.replace('\\r\\n', '\n').replace('\r\n', '\n').strip()
            if value
            else ''
        )

    def extract_table_data(self, sql: str, table_name: str) -> List[List[str]]:
        """Извлекает данные таблицы из SQL."""
        pattern = (
            rf'INSERT\s+INTO\s+[`\"]?{table_name}'
            r'[`\"]?\s*\([^)]+\)\s*VALUES\s*'
        )
        all_tuples = []
        expected_fields = EXPECTED_FIELDS.get(table_name, 15)
        for match in re.finditer(pattern, sql, re.IGNORECASE):
            values_block = self._extract_values_block(sql, match.end())
            tuples = self._parse_values_block(values_block, expected_fields)
            all_tuples.extend(tuples)
        return all_tuples

    def _extract_values_block(self, sql: str, start: int) -> str:
        """Извлекает блок VALUES из SQL."""
        in_string = False
        escape = False
        paren_level = 0
        for i, char in enumerate(sql[start:], start):
            if escape:
                escape = False
                continue
            if char == '\\':
                escape = True
                continue
            if char == "'":
                in_string = not in_string
            if not in_string:
                if char == '(':
                    paren_level += 1
                elif char == ')':
                    paren_level -= 1
                elif char == ';' and paren_level == 0:
                    return sql[start:i]
        return sql[start:]

    def _parse_values_block(
        self, values_block: str, expected_fields: int = 15
    ) -> List[List[str]]:
        """Парсит блок VALUES."""
        result = []
        current = []
        field = ''
        in_string = False
        escape = False
        paren_level = 0
        for char in values_block:
            if escape:
                field += char
                escape = False
            elif char == '\\':
                field += char
                escape = True
            elif char == "'":
                in_string = not in_string
                field += char
            elif char == ',' and not in_string and paren_level == 1:
                current.append(field.strip())
                field = ''
            elif char == '(' and not in_string:
                paren_level += 1
                if paren_level == 1:
                    field = ''
                    current = []
            elif char == ')' and not in_string:
                paren_level -= 1
                current.append(field.strip())
                field = ''
                if paren_level == 0 and len(current) == expected_fields:
                    result.append(current)
            else:
                field += char
        return result


class NewsProcessor:
    """Обработчик создания новостей."""

    def __init__(self, images_dir: str, stdout):
        """Инициализация обработчика создания новостей."""
        self.images_dir = images_dir
        self.stdout = stdout
        self.parser = SQLParser()

    def process_news(
        self, news_data: List[str], project_map: Dict[str, str]
    ) -> Optional[News]:
        """Создает объект новости из данных."""
        (
            nid,
            ntype,
            title,
            short_text,
            detail_text,
            img_url,
            date,
            gallery,
            video,
            ext_url,
            section_name,
            section_url,
            longread,
            code,
            project_id,
        ) = news_data
        if self.parser.safe_str(ntype) in SKIP_DIRECTIONS:
            return None
        news = News(
            title=self.parser.safe_str(self.parser.clean_text(title)),
            date=self.parser.safe_date(date),
            summary=self.parser.safe_str(self.parser.clean_text(short_text)),
            full_text=self.parser.safe_str(
                self.parser.clean_text(detail_text)
            ),
            detail_page_type=self._get_detail_page_type(ext_url, detail_text),
            detail_page_link=self.parser.safe_str(ext_url),
            video_url=self.parser.safe_str(video),
            project=self._get_project(project_id, project_map),
            show_on_main=True,
        )
        self._set_photo(news, img_url)
        news.save()
        self._set_directions(news, ntype)
        self._create_gallery(news, gallery)
        return news

    def _get_detail_page_type(
        self, ext_url: str, detail_text: str
    ) -> tuple[str, str]:
        """Определяет тип детальной страницы."""
        ext_url = self.parser.safe_str(ext_url)
        detail_text = self.parser.clean_text(detail_text)
        if ext_url:
            return News.DetailPageChoices.LINK
        if detail_text:
            return News.DetailPageChoices.CREATE
        return News.DetailPageChoices.NONE

    def _get_project(
        self, project_id: str, project_map: Dict[str, str]
    ) -> Optional[Project]:
        """Получает проект по ID."""
        old_pid = self.parser.safe_str(project_id)
        if old_pid in project_map:
            return Project.objects.filter(title=project_map[old_pid]).first()
        return None

    def _set_photo(self, news: News, img_url: str):
        """Устанавливает фото для новости."""
        img = self.parser.safe_str(img_url).lstrip('/').strip()
        if not img:
            return
        photo_path = os.path.join(self.images_dir, img)
        if os.path.isfile(photo_path):
            with open(photo_path, 'rb') as f:
                news.photo.save(os.path.basename(img), File(f), save=False)

    def _set_directions(self, news: News, ntype: str):
        """Устанавливает направления для новости."""
        directions_value = self.parser.safe_str(ntype)
        if not directions_value:
            return
        directions = []
        for direction_index in directions_value.split(','):
            direction_index = direction_index.strip()
            if direction_index and direction_index in DIRECTION_MAP:
                direction = Direction.objects.filter(
                    name=DIRECTION_MAP[direction_index]
                ).first()
                if direction:
                    directions.append(direction)
        if directions:
            news.directions.set(directions)

    def _create_gallery(self, news: News, gallery: str):
        """Создает галерею для новости."""
        gal = self.parser.safe_str(gallery)
        if not gal:
            return
        for img_path in re.split(r'[;,]', gal):
            img_path = img_path.replace(r'\r\n', '').strip().lstrip('/')
            if not img_path:
                continue
            if img_path.startswith(('http://', 'https://')):
                self._download_gallery_image(news, img_path)
            else:
                self._load_local_gallery_image(news, img_path)

    def _download_gallery_image(self, news: News, img_url: str):
        """Скачивает изображение из интернета."""
        try:
            resp = requests.get(img_url, timeout=10)
            if resp.status_code == 200:
                img_filename = os.path.basename(img_url.split('?')[0])
                gal_img = GalleryImage(news=news, name=img_filename)
                gal_img.image.save(
                    img_filename, ContentFile(resp.content), save=True
                )
            else:
                self.stdout.write(
                    f'Не удалось скачать {img_url} (статус {resp.status_code})'
                )
        except Exception as e:
            self.stdout.write(f'Ошибка скачивания {img_url}: {e}')

    def _load_local_gallery_image(self, news: News, img_path: str):
        """Загружает локальное изображение."""
        full_path = os.path.join(self.images_dir, img_path)
        if os.path.isfile(full_path):
            with open(full_path, 'rb') as f:
                img_filename = os.path.basename(img_path)
                gal_img = GalleryImage(news=news, name=img_filename)
                gal_img.image.save(img_filename, File(f), save=True)
        else:
            self.stdout.write(f'Файл галереи {img_path} не найден')


class Command(BaseCommand):
    """Django management-команда для импорта новостей из SQL-дампа."""

    help = 'Импортирует новости из SQL-дампа'

    def handle(self, *args, **options):
        """Основной метод выполнения команды."""
        sql_path = 'data/dump.sql'
        images_dir = 'media_data/'
        with open(sql_path, encoding='utf-8') as f:
            sql = f.read()
        parser = SQLParser()
        processor = NewsProcessor(images_dir, self.stdout)
        project_map = self._load_projects(parser, sql)
        GalleryImage.objects.all().delete()
        News.objects.all().delete()
        count = 0
        news_data_list = parser.extract_table_data(sql, 'news')
        for news_data in news_data_list:
            news = processor.process_news(news_data, project_map)
            if news:
                self.stdout.write(
                    self.style.SUCCESS(f'Новость "{news.title}" импортирована')
                )
                count += 1
        self.stdout.write(
            self.style.SUCCESS(f'Импорт завершён. Всего новостей: {count}')
        )

    def _load_projects(self, parser: SQLParser, sql: str) -> Dict[str, str]:
        """Загружает карту проектов."""
        project_map = {}
        projects_data = parser.extract_table_data(sql, 'projects')
        for pid, sort, name, description in projects_data:
            project_map[parser.safe_str(pid)] = parser.safe_str(name)
        return project_map
