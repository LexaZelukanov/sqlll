# ShopAPI — Веб-приложение на Django с MySQL

Проект демонстрирует работу с MySQL через хранимые процедуры и функции, без использования Django ORM для бизнес-логики.

## Требования
- Python 3.11+
- MySQL 8.0+
- pip

## Развёртывание БД
1. Откройте клиент MySQL (например, HeidiSQL или командную строку).
2. Выполните скрипты по порядку:
   - `sql/schema.sql` — создание БД и таблиц.
   - `sql/functions.sql` — создание функций.
   - `sql/procedures.sql` — создание процедур.
   - `sql/seed.sql` — тестовые данные.

## Установка зависимостей
```bash
pip install django mysqlclient python-dotenv

cоздайте файл .env в корне проекта (рядом с manage.py):

text
DB_NAME=shop_django
DB_USER=root
DB_PASSWORD=ваш_пароль
DB_HOST=127.0.0.1
DB_PORT=3306

Запуск проекта

python manage.py migrate --fake-initial
python manage.py runserver