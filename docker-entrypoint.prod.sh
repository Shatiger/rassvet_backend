#!/usr/bin/env bash
set -euo pipefail

echo "Ожидание PostgreSQL..."
: "${POSTGRES_HOST:=${DB_HOST:-db}}"
: "${POSTGRES_PORT:=5432}"
: "${POSTGRES_DB:=postgres}"
: "${POSTGRES_USER:=postgres}"
: "${POSTGRES_PASSWORD:=}"

until PGPASSWORD="$POSTGRES_PASSWORD" \
  psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' >/dev/null 2>&1; do
  echo "PostgreSQL ещё недоступен — ждём..."
  sleep 1
done
echo "PostgreSQL запущен"

echo "Проверка настроек..."
python manage.py check --deploy || true

echo "Миграции..."
python manage.py migrate --noinput

mkdir -p /app/static /app/media
chown -R app:app /app/static /app/media
echo "Сбор статических..."
python manage.py collectstatic --noinput

if [[ -n "${DJANGO_SUPERUSER_USERNAME:-}" && -n "${DJANGO_SUPERUSER_PASSWORD:-}" && -n "${DJANGO_SUPERUSER_EMAIL:-}" ]]; then
  echo "Создаю суперпользователя..."
  python manage.py createsuperuser --noinput || true
fi

echo "Старт приложения..."
exec gosu app:app "$@"
