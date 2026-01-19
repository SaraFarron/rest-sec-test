"""
Pydantic схемы для валидации данных.
"""
from typing import Optional
from pydantic import BaseModel, Field, field_validator


# ==================== Building Schemas ====================

class BuildingBase(BaseModel):
    """Базовая схема здания."""
    address: str = Field(..., min_length=1, max_length=500, description="Адрес здания")
    latitude: float = Field(..., ge=-90, le=90, description="Широта")
    longitude: float = Field(..., ge=-180, le=180, description="Долгота")


class BuildingCreate(BuildingBase):
    """Схема для создания здания."""
    pass


class BuildingResponse(BuildingBase):
    """Схема ответа для здания."""
    id: int

    class Config:
        from_attributes = True


# ==================== Activity Schemas ====================

class ActivityBase(BaseModel):
    """Базовая схема деятельности."""
    name: str = Field(..., min_length=1, max_length=255, description="Название деятельности")
    parent_id: Optional[int] = Field(None, description="ID родительской деятельности")


class ActivityCreate(ActivityBase):
    """Схема для создания деятельности."""
    pass


class ActivityResponse(BaseModel):
    """Схема ответа для деятельности."""
    id: int
    name: str
    parent_id: Optional[int]
    level: int

    class Config:
        from_attributes = True


class ActivityWithChildren(ActivityResponse):
    """Схема деятельности с дочерними элементами."""
    children: list["ActivityWithChildren"] = []


# ==================== Organization Schemas ====================

class OrganizationBase(BaseModel):
    """Базовая схема организации."""
    name: str = Field(..., min_length=1, max_length=500, description="Название организации")
    phone_numbers: list[str] = Field(
        ..., min_length=1, description="Список телефонов (минимум один)"
    )
    building_id: int = Field(..., description="ID здания")
    activity_ids: list[int] = Field(
        default=[], description="Список ID деятельностей"
    )

    @field_validator("phone_numbers")
    @classmethod
    def validate_phone_numbers(cls, v: list[str]) -> list[str]:
        """Проверка, что есть хотя бы один телефон."""
        if not v:
            raise ValueError("Должен быть указан хотя бы один номер телефона")
        return v


class OrganizationCreate(OrganizationBase):
    """Схема для создания организации."""
    pass


class OrganizationUpdate(BaseModel):
    """Схема для обновления организации."""
    name: Optional[str] = Field(None, min_length=1, max_length=500)
    phone_numbers: Optional[list[str]] = Field(None, min_length=1)
    building_id: Optional[int] = None
    activity_ids: Optional[list[int]] = None


class OrganizationResponse(BaseModel):
    """Схема ответа для организации."""
    id: int
    name: str
    phone_numbers: list[str]
    building: BuildingResponse
    activities: list[ActivityResponse]

    class Config:
        from_attributes = True


class OrganizationListResponse(BaseModel):
    """Схема для списка организаций."""
    id: int
    name: str
    phone_numbers: list[str]
    building_id: int

    class Config:
        from_attributes = True


# ==================== Query Schemas ====================

class GeoRadiusQuery(BaseModel):
    """Схема для поиска в радиусе от точки."""
    latitude: float = Field(..., ge=-90, le=90, description="Широта центра")
    longitude: float = Field(..., ge=-180, le=180, description="Долгота центра")
    radius_km: float = Field(..., gt=0, le=1000, description="Радиус в километрах")


class GeoBoundingBoxQuery(BaseModel):
    """Схема для поиска в прямоугольной области."""
    min_lat: float = Field(..., ge=-90, le=90, description="Минимальная широта")
    max_lat: float = Field(..., ge=-90, le=90, description="Максимальная широта")
    min_lon: float = Field(..., ge=-180, le=180, description="Минимальная долгота")
    max_lon: float = Field(..., ge=-180, le=180, description="Максимальная долгота")

    @field_validator("max_lat")
    @classmethod
    def validate_lat_range(cls, v: float, info) -> float:
        """Проверка корректности диапазона широт."""
        if "min_lat" in info.data and v < info.data["min_lat"]:
            raise ValueError("max_lat должна быть >= min_lat")
        return v

    @field_validator("max_lon")
    @classmethod
    def validate_lon_range(cls, v: float, info) -> float:
        """Проверка корректности диапазона долгот."""
        if "min_lon" in info.data and v < info.data["min_lon"]:
            raise ValueError("max_lon должна быть >= min_lon")
        return v


# ==================== Error Schemas ====================

class ErrorResponse(BaseModel):
    """Схема ответа при ошибке."""
    detail: str


class ValidationErrorResponse(BaseModel):
    """Схема ответа при ошибке валидации."""
    detail: list[dict]
