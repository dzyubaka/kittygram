# Kittygram API

## Установка и запуск (локально)

1. Клонировать репозиторий:
   git clone https://github.com/dzyubaka/kittygram

2. Создать виртуальное окружение:
   python -m venv venv
   venv\Scripts\activate  (Windows)
   source venv/bin/activate (Linux/Mac)

3. Установить зависимости:
   pip install -r requirements.txt

4. Применить миграции:
   python manage.py migrate

5. Запустить сервер:
   python manage.py runserver

6. Открыть документацию:
   http://127.0.0.1:8000/api/docs/

## Переменные окружения

Скопируйте `.env.example` в `.env` и заполните значения.
