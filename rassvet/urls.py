"""Конфигурация URL для проекта 'АПЦ Рассвет'.

Этот модуль определяет все URL-маршруты проекта, включая:
- Маршруты административной панели Django и восстановления пароля
- Маршруты для API приложений
- Маршруты для редактора CKEditor 5
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import include, path

from content.admin import admin_site

urlpatterns = [
    path(
        'admin/password_reset/',
        auth_views.PasswordResetView.as_view(),
        name='admin_password_reset',
    ),
    path(
        'admin/password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(),
        name='password_reset_done',
    ),
    path(
        'admin/reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(),
        name='password_reset_confirm',
    ),
    path(
        'admin/reset/done/',
        auth_views.PasswordResetCompleteView.as_view(),
        name='password_reset_complete',
    ),
    path('admin/', admin_site.urls),
    path('api/v1/forms/', include('form_sender.urls')),
    path('api/', include('content.urls')),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
]
if settings.DEBUG:
    urlpatterns = [
        path('__debug__/', include('debug_toolbar.urls'))
    ] + urlpatterns
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
