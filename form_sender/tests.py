"""Тесты приложения form_sender.

Покрывают:
- валидаторы телефона и имени;
- сериализатор формы обратной связи (форматирование телефона, accept_terms);
- эндпоинт POST /api/v1/forms/feedback/ (успех и ошибки валидации).
"""

import os
from unittest import mock

from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import serializers
from rest_framework.test import APITestCase

from form_sender.serializers import FeedbackFormSerializer
from form_sender.validators import (
    validate_name_characters,
    validate_phone_number,
)


class PhoneValidatorTests(TestCase):
    """Тесты валидатора номера телефона."""

    def test_valid_formats(self):
        """Корректные форматы номера проходят валидацию."""
        for value in (
            '+79161234567',
            '+7 916 123 45 67',
            '+7-916-123-45-67',
            '+7(916)123-45-67',
        ):
            with self.subTest(value=value):
                self.assertEqual(validate_phone_number(value), value)

    def test_invalid_formats(self):
        """Некорректные номера отклоняются."""
        for value in (
            '89161234567',       # без +7
            '+7916123456',       # мало цифр
            '+791612345678',     # много цифр
            '+1 916 123 45 67',  # не российский код
            'abc',
        ):
            with self.subTest(value=value):
                with self.assertRaises(serializers.ValidationError):
                    validate_phone_number(value)


class NameValidatorTests(TestCase):
    """Тесты валидатора имени."""

    def test_valid_names(self):
        """Допустимые символы проходят валидацию."""
        valid = ('Иван', 'John Doe', 'Анна-Мария', 'ООО (Тест)', "O'Neil")
        for value in valid:
            with self.subTest(value=value):
                self.assertEqual(validate_name_characters(value), value)

    def test_invalid_names(self):
        """Запрещённые символы отклоняются."""
        for value in ('Иван!', 'name@example', 'test#1', '<script>'):
            with self.subTest(value=value):
                with self.assertRaises(serializers.ValidationError):
                    validate_name_characters(value)


class FeedbackFormSerializerTests(TestCase):
    """Тесты сериализатора формы обратной связи."""

    @staticmethod
    def _payload(**overrides):
        data = {
            'name': 'Иван',
            'phone_number': '+79161234567',
            'message': 'Здравствуйте',
            'accept_terms': True,
        }
        data.update(overrides)
        return data

    def test_phone_is_normalized(self):
        """Телефон приводится к формату +7 (XXX) XXX-XX-XX."""
        serializer = FeedbackFormSerializer(
            data=self._payload(phone_number='+7 916 123 45 67')
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(
            serializer.validated_data['phone_number'],
            '+7 (916) 123-45-67',
        )

    def test_accept_terms_required_true(self):
        """Без согласия на обработку данных форма невалидна."""
        serializer = FeedbackFormSerializer(
            data=self._payload(accept_terms=False)
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('accept_terms', serializer.errors)

    def test_message_max_length(self):
        """Сообщение длиннее 1000 символов отклоняется."""
        serializer = FeedbackFormSerializer(
            data=self._payload(message='a' * 1001)
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('message', serializer.errors)


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    },
)
class FeedbackEndpointTests(APITestCase):
    """Интеграционные тесты эндпоинта формы обратной связи."""

    def setUp(self):
        """Подготавливает URL эндпоинта обратной связи."""
        self.url = reverse('feedback_form')

    @mock.patch.dict(os.environ, {'EMAIL_SEND': 'autism@rassvet-apc.ru'})
    def test_post_valid_sends_email(self):
        """Валидная заявка возвращает 200 и отправляет письмо."""
        response = self.client.post(
            self.url,
            {
                'name': 'Иван',
                'phone_number': '+79161234567',
                'message': 'Здравствуйте',
                'accept_terms': True,
            },
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(len(mail.outbox), 1)

    def test_post_invalid_returns_400(self):
        """Невалидная заявка возвращает 400 и не отправляет письмо."""
        response = self.client.post(
            self.url,
            {
                'name': 'Иван!',
                'phone_number': 'bad',
                'message': '',
                'accept_terms': False,
            },
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(mail.outbox), 0)
