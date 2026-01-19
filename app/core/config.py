from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Настройки приложения."""
    
    # Основные настройки
    APP_NAME: str = "Organization Directory API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # База данных (SQLite по умолчанию для локальной разработки)
    DATABASE_URL: str = "sqlite:///./directory.db"
    
    # Безопасность
    API_KEY: str = "secret-api-key-change-in-production"
    API_KEY_HEADER: str = "X-API-KEY"
    
    # Логирование
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Получение настроек приложения (кэшируется)."""
    return Settings()
