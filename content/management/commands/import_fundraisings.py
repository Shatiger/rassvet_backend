"""Django management команда для импорта данных сборов средств."""

from typing import Any

from content.management.config import MODEL_CONFIG
from content.management.utils import ImporterBase
from content.models import (
    FundraisingPhoto,
    TargetedFundraising,
)


class Command(ImporterBase):
    """Команда Django для импорта данных целевых сборов средств."""

    help = 'Импорт благодарностей из TXT-файла'
    model_class = TargetedFundraising
    file_path = 'fundraisings.txt'
    model_config: Any = MODEL_CONFIG[model_class]

    def post_process_instance(self, instance, row, row_num):
        """Выполняет дополнительную обработку после создания целевого сбора."""
        self._process_photos(instance, row)
        return True

    def _process_photos(self, instance, row):
        """Обрабатывает фотографии для целевого сбора."""
        for i in range(1, 4):
            if photo_path := row.get(f'photo{i}'):
                self._create_photo(instance, photo_path)

    def _create_photo(self, instance, path):
        """Создает и сохраняет фотографию для целевого сбора."""
        photo = FundraisingPhoto(
            fundraising=instance,
        )
        photo.save()
        if self.save_file_to_model(photo, path, 'image'):
            self.stdout.write(f"Загружено фото для сбора '{instance.title}'")
