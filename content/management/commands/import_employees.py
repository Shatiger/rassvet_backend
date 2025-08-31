"""Django management команда для импорта сотрудников."""

import csv
from typing import Any

from content.management.config import MODEL_CONFIG
from content.management.utils import ImporterBase
from content.models import Document, Employee, TypeDocument


class Command(ImporterBase):
    """Команда Django для импорта сотрудников и их документов из CSV-файла.

    Импортирует данные сотрудников, их изображения и связанные документы.
    """

    help = 'Импорт сотрудников и их документов из CSV-файла'
    model_class = Employee
    file_path = 'employees.txt'
    use_transaction = True
    model_config: Any = MODEL_CONFIG[model_class]
    employees_cache: dict[str, Employee] = {}

    def _validate_row(self, row_num: int, row: dict) -> bool:
        """Проверка валидности данных строки CSV перед импортом."""
        name = row.get('name', '').strip()
        if not name:
            self.handle_error('Отсутствует имя сотрудника', row_num)
            return False
        if any(
            row.get(field) for field in ['specialities', 'main_specialities']
        ):
            order = row.get('order')
            if not order or not str(order).strip().isdigit():
                row['order'] = '999'
        return True

    def create_or_get_employee(
        self, row: dict, row_num: int
    ) -> Employee | None:
        """Создает нового сотрудника или возвращает существующего из кэша."""
        name = row.get('name', '').strip()
        if not name:
            return None
        if name not in self.employees_cache:
            if any(
                row.get(field)
                for field in ['specialities', 'main_specialities']
            ):
                instance = self.create_instance(row, row_num)
                if instance:
                    self.employees_cache[name] = instance
                    image_path = row.get('image')
                    if image_path:
                        self.save_file_to_model(
                            instance=instance,
                            file_path=image_path,
                            field_name='image',
                        )
        return self.employees_cache.get(name)

    def process_document(
        self, instance: Employee, row: dict, row_num: int
    ) -> bool:
        """Обрабатывает документы сотрудника из данных строки CSV."""
        try:
            for field_name, field_value in row.items():
                if (
                    not field_value
                    or field_name == 'image'
                    or not isinstance(field_value, str)
                    or not field_value.startswith('/images/')
                ):
                    continue
                fields = list(row.values())
                field_idx = list(row.keys()).index(field_name)
                doc_type = (
                    fields[field_idx + 1]
                    if field_idx + 1 < len(fields)
                    else ''
                )
                on_main = doc_type.lower().strip() == 'лента'
                doc_type_instance = None
                if doc_type and not on_main:
                    doc_type_instance, _ = TypeDocument.objects.get_or_create(
                        name=doc_type
                    )
                document = Document.objects.create(
                    employee=instance,
                    type=doc_type_instance,
                    on_main_page=on_main,
                )
                self.save_file_to_model(
                    instance=document,
                    file_path=field_value.strip(),
                    field_name='file',
                )
            return True
        except Exception as e:
            self.handle_error(
                f'Ошибка при создании документа: {str(e)}', row_num
            )
            return False

    def import_data(self, *args, **kwargs) -> int:
        """Импортирует данные сотрудников и их документов."""
        success_count = 0
        data_path = self.get_data_path(self.file_path)
        with open(data_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=self.delimiter)
            for row_num, row in enumerate(reader, 1):
                if not self._validate_row(row_num, row):
                    continue
                try:
                    instance = self.create_or_get_employee(row, row_num)
                    if not instance:
                        continue
                    if self.process_document(instance, row, row_num):
                        success_count += 1
                except Exception as e:
                    self.handle_error(
                        f'Ошибка в строке {row_num}: {str(e)}', row_num
                    )
        return success_count
