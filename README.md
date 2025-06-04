# URL Shortener Service

REST API-сервис для сокращения длинных URL в короткие ссылки с поддержкой статистики, деактивации и сроком действия.

## Возможности

- Сокращение длинных URL в короткий код
- Перенаправление по короткой ссылке на оригинальный URL
- Срок действия ссылки — 1 день
- Деактивация ссылок (без удаления из БД)
- Статистика переходов по ссылкам
- Basic-аутентификация для защищённых эндпоинтов
- Swagger-документация по адресу `/docs`
- Поддержка фильтрации, пагинации и сортировки по кликам

## Технологии

- Python 3.10
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic

## Установка и запуск

1. Клонируйте репозиторий:

- `git clone https://github.com/your-username/url-shortener.git`
- `cd url-shortener`

2.Создайте и активируйте виртуальное окружение (можно пропустить этот шаг):

- `python -m venv venv`
- `source venv/bin/activate`  для Windows: `venv\Scripts\activate`

3. Установите зависимости:

- `pip install -r requirements.txt`

4. Инициализируйте базу данных:
Убедитесь, что PostgreSQL запущен и данные подключения заданы в app/database.py.

- `python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"`

5. Запустите приложение:

- `uvicorn app.main:app --reload`

## Аутентификация

Приватные эндпоинты защищены Basic Auth:

Username: admin

Password: admin123

## Документация

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Эндпоинты

- POST /api/shorten — создать короткую ссылку
- GET /{short_code} — перейти по короткой ссылке
- POST /api/deactivate/{short_code} — деактивировать ссылку
- GET /api/links — получить список ссылок
- GET /api/statistics — получить статистику по переходам
