"""
Главный модуль FastAPI приложения.
Organization Directory API - справочник организаций, зданий и деятельностей.
"""
import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.config import get_settings
from app.routers import buildings_router, activities_router, organizations_router

# Настройка логирования
settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle менеджер приложения."""
    logger.info("Starting Organization Directory API...")
    yield
    logger.info("Shutting down Organization Directory API...")


# Создание приложения
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## Organization Directory API

REST API сервис-справочник для управления:
- **Организациями** - компании с телефонами, зданием и видами деятельности
- **Зданиями** - адреса и географические координаты
- **Деятельностями** - иерархическая структура видов деятельности (до 3 уровней)

### Аутентификация
Все эндпоинты защищены API-ключом. Передавайте ключ в заголовке `X-API-KEY`.

### Основные возможности
- Поиск организаций по зданию, деятельности, названию
- Геопоиск: в радиусе от точки или в прямоугольной области
- Иерархический поиск по деятельности с учетом дочерних категорий
    """,
    openapi_tags=[
        {"name": "Buildings", "description": "Операции со зданиями"},
        {"name": "Activities", "description": "Операции с видами деятельности"},
        {"name": "Organizations", "description": "Операции с организациями"},
    ],
    lifespan=lifespan,
)


# Middleware для логирования запросов
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Логирование всех HTTP запросов."""
    start_time = time.time()
    
    # Логируем входящий запрос
    logger.info(f"Request: {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    # Логируем время выполнения
    process_time = time.time() - start_time
    logger.info(
        f"Response: {request.method} {request.url.path} "
        f"- Status: {response.status_code} - Time: {process_time:.3f}s"
    )
    
    return response


# Обработчик ошибок валидации
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Обработка ошибок валидации Pydantic."""
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


# Глобальный обработчик исключений
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Глобальный обработчик непредвиденных ошибок."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


# Подключение роутеров
app.include_router(buildings_router, prefix="/api/v1")
app.include_router(activities_router, prefix="/api/v1")
app.include_router(organizations_router, prefix="/api/v1")


# Health check эндпоинт (без аутентификации)
@app.get(
    "/health",
    tags=["Health"],
    summary="Проверка состояния сервиса",
)
def health_check():
    """Эндпоинт для проверки работоспособности сервиса."""
    return {"status": "healthy", "version": settings.APP_VERSION}


@app.get(
    "/",
    tags=["Health"],
    summary="Корневой эндпоинт",
)
def root():
    """Корневой эндпоинт с информацией о сервисе."""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
    }
