"""Модуль конфигурации административного интерфейса для приложения users.

Этот модуль регистрирует модели приложения пользователей в административном
интерфейсе Django и настраивает отображение, фильтрацию и редактирование
пользовательских данных.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import RassvetUser
from content.admin.site import admin_site


@admin.register(RassvetUser, site=admin_site)
class RassvetUserAdmin(UserAdmin):
    """Административный интерфейс для модели пользователя RassvetUser."""

    pass
