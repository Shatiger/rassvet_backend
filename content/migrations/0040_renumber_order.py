"""Перенумерация поля order: убирает дубли значений.

Модели переводили с OrderMixin (default=0) на OrderedModel обычными
AlterField, без переноса данных, поэтому у записей, созданных до этого,
order остался нулевым. Дубли делают сортировку неоднозначной: в API
порядок при равных order произвольный, а стрелки "вверх/вниз" в админке
не работают, потому что previous()/next() ищут соседа строгим сравнением
order и внутри группы одинаковых значений соседа не находят.

Миграция раздаёт order значения 0..n-1 по возрастанию id. Нумерация
с нуля — её же ожидает OrderedModel: get_next_order() для пустой группы
возвращает 0, дальше max+1.

Модель, у которой дублей нет, не трогается вовсе. Это защита от повторного
применения: если миграцию откатят (обратная операция noop, отметка о
применении снимается) и накатят заново, расставленный руками порядок
не сбросится.
"""

from django.db import migrations
from django.db.models import Count

BATCH_SIZE = 500


def _has_duplicates(model, db_alias, group_field=None):
    """Проверяет, есть ли записи с одинаковым order."""
    group_by = [group_field, 'order'] if group_field else ['order']
    return (
        model.objects.using(db_alias)
        .values(*group_by)
        .annotate(total=Count('id'))
        .filter(total__gt=1)
        .exists()
    )


def _renumber(model, db_alias, order_by, group_field=None):
    """Раздаёт order значения 0..n-1 в порядке order_by.

    Если задан group_field, нумерация идёт независимо внутри каждой
    группы (для Report это раздел, см. order_with_respect_to).
    Модель без дублей order остаётся без изменений.
    """
    if not _has_duplicates(model, db_alias, group_field):
        return 0

    fields = ['id', 'order']
    if group_field:
        fields.append(group_field)
    objects = list(
        model.objects.using(db_alias).only(*fields).order_by(*order_by)
    )

    changed = []
    current_group = object()
    index = 0
    for obj in objects:
        if group_field:
            group = getattr(obj, group_field)
            if group != current_group:
                current_group = group
                index = 0
        if obj.order != index:
            obj.order = index
            changed.append(obj)
        index += 1

    if changed:
        model.objects.using(db_alias).bulk_update(
            changed, ['order'], batch_size=BATCH_SIZE
        )
    return len(changed)


def renumber_order(apps, schema_editor):
    """Перенумеровывает order у партнёров, проектов, разделов и отчётов."""
    db_alias = schema_editor.connection.alias
    for model_name in ('Partner', 'Project', 'Chapter'):
        _renumber(
            apps.get_model('content', model_name),
            db_alias,
            order_by=('id',),
        )
    _renumber(
        apps.get_model('content', 'Report'),
        db_alias,
        order_by=('chapter_id', 'id'),
        group_field='chapter_id',
    )


class Migration(migrations.Migration):
    dependencies = [
        ('content', '0039_alter_link_fields_and_report_file'),
    ]

    operations = [
        migrations.RunPython(renumber_order, migrations.RunPython.noop),
    ]
