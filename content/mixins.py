"""Модуль содержит миксины для классов."""

from typing import Optional, Type

from django.contrib import admin
from django.db import models, transaction
from django.db.models import FileField
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.urls import path
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

from ordered_model.models import OrderedModel
from rest_framework.serializers import Serializer

from .constants import ORDER_DEFAULT, TITLE_LENGTH


class TitleMixin(models.Model):
    """Абстрактная модель для добавления поля заголовка."""

    title = models.CharField('Заголовок', max_length=TITLE_LENGTH)

    class Meta:
        """Мета-класс для указания того, что модель является абстрактной."""

        abstract = True


class TimestampMixin(models.Model):
    """Абстрактная модель для добавления временных меток."""

    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        """Мета-класс для указания того, что модель является абстрактной."""

        abstract = True


class OrderMixin(models.Model):
    """Абстрактная модель для добавления поля порядка отображения."""

    order = models.PositiveSmallIntegerField(
        'Порядок отображения',
        default=ORDER_DEFAULT,
        help_text='Чем меньше значение, тем первее в списке',
    )

    class Meta:
        """Мета-класс для указания того, что модель является абстрактной."""

        abstract = True


class CleanEmptyHTMLMixin:
    """Миксин для автоматической очистки HTML-полей от "пустых" значений."""

    clean_html_fields: tuple[str, ...] = ()

    def save(self, *args, **kwargs):
        """Переопределяет сохранение объекта: очищает указанные HTML-поля."""
        for field in self.clean_html_fields:
            original_field = getattr(self, field, None)
            setattr(self, field, self._clean_empty_html(original_field))
        super().save(*args, **kwargs)

    def _clean_empty_html(self, raw_html):
        """Проверяет значение HTML-поля.

        Если значение поля ровно <p>&nbsp;</p> (или <p> </p>), возвращает None.
        В остальных случаях возвращает оригинальное значение.
        """
        if raw_html is None:
            return ''
        cleared = raw_html.strip().replace('\xa0', '&nbsp;')
        if cleared == '<p>&nbsp;</p>':
            return ''
        return raw_html


class MultiSerializerViewSetMixin:
    """Миксин для выбора подходящего сериализатора из `serializer_classes`."""

    serializer_classes: Optional[dict[str, Type[Serializer]]] = None

    def get_serializer_class(self):
        """Выбирает сериализатор из словаря по действию."""
        try:
            return self.serializer_classes[self.action]
        except (KeyError, TypeError):
            return super().get_serializer_class()


class CharCountAdminMixin(admin.ModelAdmin):
    """Миксин для Django Admin, добавляющий подсчёт символов."""

    charcount_fields: dict[str, int | dict[str, int]] = {}

    class Media:
        js = ('custom_admin/js/char_count.js',)
        css = {'all': ('custom_admin/css/char_count.css',)}

    def get_form(self, request, obj=None, **kwargs):
        """Переопределяет метод get_form.

        Позволяет:
        1. Проставить data-атрибуты в HTML-виджетах выбранных полей.
        2. Добавить help_text с рекомендациями по количеству символов.
        """
        form = super().get_form(request, obj, **kwargs)
        cfg = getattr(self, 'charcount_fields', {}) or {}

        for name, limits in cfg.items():
            if name not in form.base_fields:
                continue
            base_field = form.base_fields[name]
            base_field.widget.attrs['data-charcount'] = '1'

            min_value = max_value = None
            if isinstance(limits, int):
                max_value = limits
            elif isinstance(limits, dict):
                min_value = limits.get('min')
                max_value = limits.get('max')

            if min_value is not None:
                base_field.widget.attrs['data-min'] = str(min_value)
            if max_value is not None:
                base_field.widget.attrs['data-max'] = str(max_value)

        return form


class VideoOrientationMixin(models.Model):
    """Миксин с перечислением ориентаций и хелпером для max_length."""

    class VideoOrientationChoices(models.TextChoices):
        HORIZONTAL = 'horizontal', 'Горизонтальная'
        VERTICAL = 'vertical', 'Вертикальная'

    @classmethod
    def video_orientation_max_length(cls) -> int:
        """Максимальная длина значения среди choices (для max_length)."""
        return max(
            len(value) for value, _ in cls.VideoOrientationChoices.choices
        )

    class Meta:
        abstract = True


class SafeOrderedInlineModelAdminMixin:
    """Делает безопасное массовое удаление для OrderedInline."""

    def save_formset(self, request, form, formset, change):
        """Безопасное сохранение inline для ordered моделей."""
        Model = formset.model
        if not issubclass(Model, OrderedModel):
            return super().save_formset(request, form, formset, change)
        order_field = getattr(Model, 'order_field_name', 'order')
        fk_name = formset.fk.name
        with transaction.atomic():
            instances = formset.save(commit=False)
            deleted = list(getattr(formset, 'deleted_objects', []))
            deleted.sort(
                key=lambda o: getattr(o, order_field) or 0, reverse=True
            )
            for obj in deleted:
                obj.delete()

            deleted_pks = {obj.pk for obj in deleted if obj.pk}
            parent = form.instance
            for obj in instances:
                if obj.pk and obj.pk in deleted_pks:
                    continue
                if getattr(obj, f'{fk_name}_id', None) is None:
                    setattr(obj, fk_name, parent)
                obj.save()
            formset.save_m2m()


class InstantDeleteInlineMixin:
    """Подключает кнопку 'Удалить' (через JS)."""

    class Media:
        js = (
            'admin/js/jquery.init.js',
            'custom_admin/js/inline_instant_delete.js',
        )
        css = {'all': ('custom_admin/css/instant_delete.css',)}


class InstantDeleteSingleModelAdminMixin:
    """Добавляет URL /inline-delete/<pk>/ на странице редактирования.

    Нужно указать: instant_delete_model = <Модель инлайна>(например, Document).
    Пермишен берётся автоматически: '<app>.delete_<model>'.
    """

    instant_delete_model: admin.ModelAdmin | None = None

    def get_urls(self):
        """Добавляет URL для удаления записи в общий список URL модели."""
        return [
            path(
                'inline-delete/<int:pk>/',
                self.admin_site.admin_view(self._instant_delete_view),
                name=f'{self.model._meta.app_label}_'
                f'{self.model._meta.model_name}_inline_delete',
            ),
        ] + super().get_urls()

    @method_decorator(csrf_protect)
    def _instant_delete_view(self, request, pk: int):
        if request.method != 'POST':
            return HttpResponseForbidden('POST required')

        Model = self.instant_delete_model
        assert (
            Model is not None
        ), 'Set instant_delete_model = <InlineModel> on admin'

        perm = f'{Model._meta.app_label}.delete_{Model._meta.model_name}'
        if not request.user.has_perm(perm):
            return HttpResponseForbidden('No permission')

        obj = get_object_or_404(Model, pk=pk)

        for f in obj._meta.get_fields():
            if isinstance(f, FileField):
                file = getattr(obj, f.name, None)
                if file and getattr(file, 'name', None):
                    try:
                        file.delete(save=False)
                    except Exception:
                        pass

        obj.delete()
        return JsonResponse({'ok': True, 'deleted': pk})
