# Organization Directory API

REST API сервис-справочник для управления организациями, зданиями и видами деятельности.

## Быстрый старт

### Локальный запуск через Poetry

```bash
poetry install

# Инициализировать базу данных тестовыми данными
poetry run python init_db.py

poetry run uvicorn app.main:app --reload

# API будет доступен по адресу: http://localhost:8000
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

### Запуск через Docker

```bash
docker-compose up --build

# API будет доступен по адресу: http://localhost:8000
```

### Остановка сервисов

```bash
docker-compose down

# Для полной очистки (включая данные БД):
docker-compose down -v
```

## Конфигурация

Настройки приложения задаются через переменные окружения или файл `.env`:

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `DATABASE_URL` | URL подключения к PostgreSQL | `postgresql://postgres:postgres@db:5432/directory` |
| `API_KEY` | Статический API-ключ для аутентификации | `secret-api-key-change-in-production` |
| `LOG_LEVEL` | Уровень логирования | `INFO` |
| `DEBUG` | Режим отладки | `false` |

## Аутентификация

Все эндпоинты (кроме `/health` и `/`) защищены API-ключом. 
Передавайте ключ в заголовке `X-API-KEY`:

```bash
curl -H "X-API-KEY: secret-api-key-change-in-production" http://localhost:8000/api/v1/buildings/
```

При запуске автоматически создаются тестовые данные:

### Здания (5 шт.)
- Тверская, 1 (центр Москвы)
- Арбат, 10
- Ленинский проспект, 25
- Новый Арбат, 15
- Кутузовский проспект, 32

### Организации (10 шт.)
Различные компании с разными комбинациями зданий и деятельностей.
