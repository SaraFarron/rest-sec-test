"""
Модуль инициализации схем.
"""
from app.schemas.schemas import (
    BuildingBase, BuildingCreate, BuildingResponse,
    ActivityBase, ActivityCreate, ActivityResponse, ActivityWithChildren,
    OrganizationBase, OrganizationCreate, OrganizationUpdate,
    OrganizationResponse, OrganizationListResponse,
    GeoRadiusQuery, GeoBoundingBoxQuery,
    ErrorResponse, ValidationErrorResponse,
)

__all__ = [
    "BuildingBase", "BuildingCreate", "BuildingResponse",
    "ActivityBase", "ActivityCreate", "ActivityResponse", "ActivityWithChildren",
    "OrganizationBase", "OrganizationCreate", "OrganizationUpdate",
    "OrganizationResponse", "OrganizationListResponse",
    "GeoRadiusQuery", "GeoBoundingBoxQuery",
    "ErrorResponse", "ValidationErrorResponse",
]
