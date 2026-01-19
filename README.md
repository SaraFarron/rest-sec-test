# Organization Directory API

REST API сервис-справочник для управления организациями, зданиями и видами деятельности.

## Технологический стек

- **Python 3.10+**
- **FastAPI** - веб-фреймворк
- **Pydantic** - валидация данных
- **SQLAlchemy** - ORM
- **Alembic** - миграции БД
- **PostgreSQL / SQLite** - база данных
- **Poetry** - управление зависимостями
- **Docker + Docker Compose** - контейнеризация

## Быстрый старт

### Локальный запуск через Poetry (рекомендуется для разработки)

```bash
# Установить Poetry (если не установлен)
curl -sSL https://install.python-poetry.org | python3 -

# Перейти в директорию проекта
cd rest-sec-test

# Установить зависимости
poetry install

# Инициализировать базу данных тестовыми данными
poetry run python init_db.py

# Запустить сервер в режиме разработки
poetry run uvicorn app.main:app --reload

# API будет доступен по адресу: http://localhost:8000
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

### Полезные команды Poetry

```bash
# Запуск сервера
poetry run uvicorn app.main:app --reload

# Запуск с указанием хоста и порта
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Форматирование кода
poetry run black app/
poetry run isort app/

# Проверка типов
poetry run mypy app/

# Запуск тестов
poetry run pytest

# Добавить новую зависимость
poetry add <package-name>

# Добавить dev-зависимость
poetry add --group dev <package-name>

# Обновить зависимости
poetry update
```

### Запуск через Docker (для production)

```bash
# Запустить все сервисы одной командой
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

## Структура проекта

```
rest-sec-test/
├── app/
│   ├── __init__.py
│   ├── main.py              # Точка входа FastAPI
│   ├── core/
│   │   ├── config.py        # Конфигурация приложения
│   │   ├── database.py      # Подключение к БД
│   │   └── security.py      # Проверка API-ключа
│   ├── models/
│   │   └── models.py        # SQLAlchemy модели
│   ├── schemas/
│   │   └── schemas.py       # Pydantic схемы
│   ├── repositories/
│   │   ├── building_repository.py
│   │   ├── activity_repository.py
│   │   └── organization_repository.py
│   ├── services/
│   │   └── organization_service.py
│   └── routers/
│       ├── buildings.py
│       ├── activities.py
│       └── organizations.py
├── alembic/
│   ├── env.py
│   └── versions/
│       ├── 001_initial_schema.py
│       └── 002_seed_data.py
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## Доменная модель

### Здание (Building)
- `id` - уникальный идентификатор
- `address` - адрес здания
- `latitude` - широта
- `longitude` - долгота

### Деятельность (Activity)
- `id` - уникальный идентификатор
- `name` - название
- `parent_id` - ссылка на родительскую деятельность
- `level` - уровень вложенности (1-3)

Максимальная глубина дерева: **3 уровня**.

### Организация (Organization)
- `id` - уникальный идентификатор
- `name` - название
- `phone_numbers` - список телефонов
- `building_id` - ссылка на здание
- `activities` - связь M2M с деятельностями

## API Эндпоинты

### Здания

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/v1/buildings/` | Список всех зданий |
| GET | `/api/v1/buildings/{id}` | Получить здание по ID |
| POST | `/api/v1/buildings/` | Создать здание |

### Деятельности

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/v1/activities/` | Список всех деятельностей |
| GET | `/api/v1/activities/tree` | Корневые деятельности |
| GET | `/api/v1/activities/{id}` | Получить деятельность по ID |
| POST | `/api/v1/activities/` | Создать деятельность |

### Организации

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/v1/organizations/` | Список всех организаций |
| GET | `/api/v1/organizations/{id}` | Получить организацию по ID |
| GET | `/api/v1/organizations/search?name=` | Поиск по названию |
| GET | `/api/v1/organizations/by-building/{building_id}` | Организации в здании |
| GET | `/api/v1/organizations/by-activity/{activity_id}` | Организации по деятельности |
| GET | `/api/v1/organizations/in-radius` | Организации в радиусе от точки |
| GET | `/api/v1/organizations/in-box` | Организации в прямоугольной области |
| POST | `/api/v1/organizations/` | Создать организацию |
| PUT | `/api/v1/organizations/{id}` | Обновить организацию |

## Примеры curl-запросов

### Проверка работоспособности (без аутентификации)

```bash
curl http://localhost:8000/health
```

### Получить список всех зданий

```bash
curl -H "X-API-KEY: secret-api-key-change-in-production" \
  http://localhost:8000/api/v1/buildings/
```

### Получить организацию по ID

```bash
curl -H "X-API-KEY: secret-api-key-change-in-production" \
  http://localhost:8000/api/v1/organizations/1
```

### Поиск организаций по названию

```bash
curl -H "X-API-KEY: secret-api-key-change-in-production" \
  "http://localhost:8000/api/v1/organizations/search?name=Авто"
```

### Организации в конкретном здании

```bash
curl -H "X-API-KEY: secret-api-key-change-in-production" \
  http://localhost:8000/api/v1/organizations/by-building/1
```

### Организации по виду деятельности (с учетом поддерева)

```bash
# Найти все организации с деятельностью "Еда" и всеми дочерними деятельностями
curl -H "X-API-KEY: secret-api-key-change-in-production" \
  "http://localhost:8000/api/v1/organizations/by-activity/1?include_children=true"
```

### Организации в радиусе 5 км от точки

```bash
curl -H "X-API-KEY: secret-api-key-change-in-production" \
  "http://localhost:8000/api/v1/organizations/in-radius?latitude=55.75&longitude=37.62&radius_km=5"
```

### Организации в прямоугольной области

```bash
curl -H "X-API-KEY: secret-api-key-change-in-production" \
  "http://localhost:8000/api/v1/organizations/in-box?min_lat=55.70&max_lat=55.76&min_lon=37.55&max_lon=37.65"
```

### Создать новую организацию

```bash
curl -X POST \
  -H "X-API-KEY: secret-api-key-change-in-production" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Новая компания",
    "phone_numbers": ["+7-495-123-4567"],
    "building_id": 1,
    "activity_ids": [1, 5]
  }' \
  http://localhost:8000/api/v1/organizations/
```

### Создать новую деятельность

```bash
curl -X POST \
  -H "X-API-KEY: secret-api-key-change-in-production" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Новая категория",
    "parent_id": 1
  }' \
  http://localhost:8000/api/v1/activities/
```

### Получить список деятельностей

```bash
curl -H "X-API-KEY: secret-api-key-change-in-production" \
  http://localhost:8000/api/v1/activities/
```

## Тестовые данные

При запуске автоматически создаются тестовые данные:

### Здания (5 шт.)
- Тверская, 1 (центр Москвы)
- Арбат, 10
- Ленинский проспект, 25
- Новый Арбат, 15
- Кутузовский проспект, 32

### Дерево деятельностей
```
├── Еда (level 1)
│   ├── Мясная продукция (level 2)
│   ├── Молочная продукция (level 2)
│   └── Выпечка (level 2)
│       ├── Хлеб (level 3)
│       └── Кондитерские изделия (level 3)
├── Автомобили (level 1)
│   ├── Грузовые (level 2)
│   └── Легковые (level 2)
│       ├── Запчасти (level 3)
│       ├── Аксессуары (level 3)
│       └── Шиномонтаж (level 3)
├── Услуги (level 1)
│   ├── Ремонт техники (level 2)
│   │   ├── Ремонт телефонов (level 3)
│   │   └── Ремонт компьютеров (level 3)
│   └── Юридические услуги (level 2)
└── Медицина (level 1)
    ├── Стоматология (level 2)
    └── Терапия (level 2)
```

### Организации (10 шт.)
Различные компании с разными комбинациями зданий и деятельностей.

## Обработка ошибок

API возвращает ошибки в формате JSON:

- **400** - Некорректный запрос
- **401** - Отсутствует или неверный API-ключ
- **404** - Ресурс не найден
- **422** - Ошибка валидации данных
- **500** - Внутренняя ошибка сервера

Пример ответа с ошибкой:
```json
{
  "detail": "Organization with id 999 not found"
}
```

## Архитектурные решения

1. **Слоистая архитектура**: Routers → Services → Repositories → Models
2. **Dependency Injection**: Использование FastAPI Depends для инъекции зависимостей
3. **Репозиторий паттерн**: Инкапсуляция логики работы с БД
4. **Формула Хаверсина**: Для точного расчета расстояний в геопоиске
5. **Рекурсивный обход**: Для поиска организаций по поддереву деятельностей

## Лицензия

MIT
