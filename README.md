# 💰 Финансовый трекер (FastAPI + PostgreSQL + Redis)

Веб-приложение для учёта личных финансов: управление кошельками, доходами, расходами, переводами между счетами с автоматической конвертацией валют (RUB, USD, EUR).  
Данные хранятся в PostgreSQL, для ускорения повторяющихся запросов используется Redis-кэш. Приложение полностью контейнеризировано с помощью Docker Compose.

## 🚀 Основные возможности

- Регистрация и авторизация пользователей (логин в Bearer-токене).
- Создание кошельков в разных валютах.
- Добавление доходов и расходов с указанием категории.
- Перевод средств между своими кошельками с конвертацией валют.
- Отчёт по операциям за выбранный период.
- Отображение общего баланса в рублях (с учётом курсов валют).

## 🛠 Технологии

- **Backend**: FastAPI, SQLAlchemy (async), Alembic, Pydantic
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Frontend**: HTML, Bootstrap 5, vanilla JavaScript
- **Infrastructure**: Docker, Docker Compose
- **Testing**: pytest, pytest-asyncio, httpx

## 📋 Требования

- Установленные [Docker](https://docs.docker.com/get-docker/) и [Docker Compose](https://docs.docker.com/compose/install/) (входят в Docker Desktop на Windows/Mac).
- Порт 8000 свободен (для приложения), порт 5432 (PostgreSQL) и 6379 (Redis) – могут использоваться, но необязательны для работы вне контейнера.

## ⚙️ Переменные окружения

Создайте файл `.env` в корне проекта (или используйте значения по умолчанию). Пример содержания:

```ini
POSTGRES_USER=postgres
POSTGRES_PASSWORD=mysecretpassword
POSTGRES_SERVER=postgres
POSTGRES_PORT=5432
POSTGRES_DB=finance_db
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

```
Переменные уже настроены в docker-compose.yml. Для локального запуска без Docker можно указать **POSTGRES_SERVER=localhost** и установить **PostgreSQL/Redis** вручную.

## 🐳 Запуск через Docker Compose (рекомендованный способ)
**Клонируйте репозиторий**
```
git clone https://github.com/Alexpythonenjoer/Finance_Tracker.git
```
```
cd finance-tracker
```
**Запустите все сервисы**
```
docker-compose up -d --build
```
**Будут подняты контейнеры:**
```
finance_app – FastAPI приложение

finance_db_postgres – PostgreSQL

finance_redis – Redis
```
**Выполните миграции базы данных**
```
docker-compose exec app alembic upgrade head
```
**Откройте приложение в браузере**
```
Фронтенд: http://localhost:8000/static/index.html

Swagger документация API: http://localhost:8000/docs
```
**🛑Остановка**
```
docker-compose down
```
## 🧪 Тестирование
**Тесты написаны с использованием pytest-asyncio и запускаются в локальном окружении (вне Docker).
Для их выполнения:**

Создайте виртуальное окружение (Python 3.11+) и установите зависимости:
```
python -m venv venv
source venv/bin/activate   # или venv\Scripts\activate на Windows
pip install -r requirements.txt
```
Убедитесь, что Docker-контейнеры с PostgreSQL и Redis не мешают (можно запустить тесты с подменой зависимостей на заглушки). Для простоты тесты используют асинхронный SQLite in-memory и мок-клиент Redis – дополнительная настройка не требуется.

Запустите тесты:
```
pytest -v --asyncio-mode=auto
```
## 🖥 Локальный запуск без Docker (для разработки)
Установите и запустите PostgreSQL и Redis на вашей машине.

Скопируйте ```.env.example``` в .env и отредактируйте переменные (POSTGRES_SERVER=localhost).

Установите зависимости:
```
pip install -r requirements.txt
```
Выполните миграции:
```
alembic upgrade head
```
Запустите приложение:
```

uvicorn main:app --reload
```
## 🗂 Структура проекта
```
.
├── app/
│   ├── api/            # Эндпоинты (wallets, operations, users)
│   ├── repository/     # Работа с БД (асинхронные методы)
│   ├── service/        # Бизнес-логика
│   ├── static/         # HTML, CSS, JS фронтенда
│   ├── database.py     # Настройка async engine и сессий
│   ├── models.py       # SQLAlchemy модели
│   ├── schemas.py      # Pydantic схемы для валидации
│   ├── redis_client.py # Клиент Redis (пул соединений)
│   └── dependency.py   # Зависимости: get_db, get_current_user, get_redis_client
├── alembic/            # Миграции Alembic
├── tests/              # pytest тесты
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```
## 📌 Примечания
Валютные курсы обновляются через currency-api. При недоступности API используются fallback-курсы.

В тестовом окружении Redis автоматически заменяется на мок-объект (см. redis_client.py при TESTING=true).