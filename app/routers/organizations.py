"""
Роутер для работы с организациями.
"""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core import get_db, verify_api_key
from app.services import OrganizationService
from app.schemas import (
    OrganizationResponse,
    OrganizationCreate,
    OrganizationUpdate,
    ErrorResponse,
)

router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
    dependencies=[Depends(verify_api_key)],
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
    },
)


@router.get(
    "/",
    response_model=list[OrganizationResponse],
    summary="Получить список организаций",
    description="Возвращает список всех организаций с информацией о здании и деятельностях.",
)
def get_all_organizations(
    db: Session = Depends(get_db),
) -> list[OrganizationResponse]:
    """Получить список всех организаций."""
    service = OrganizationService(db)
    return service.org_repo.get_all()


@router.get(
    "/search",
    response_model=list[OrganizationResponse],
    summary="Поиск организаций по названию",
    description="Поиск организаций по частичному совпадению названия (case-insensitive).",
    responses={
        400: {"model": ErrorResponse, "description": "Bad request"},
    },
)
def search_organizations(
    name: str = Query(..., min_length=2, description="Строка поиска (минимум 2 символа)"),
    db: Session = Depends(get_db),
) -> list[OrganizationResponse]:
    """Поиск организаций по названию."""
    service = OrganizationService(db)
    return service.search_by_name(name)


@router.get(
    "/by-building/{building_id}",
    response_model=list[OrganizationResponse],
    summary="Организации в здании",
    description="Получить список всех организаций в конкретном здании.",
    responses={
        404: {"model": ErrorResponse, "description": "Building not found"},
    },
)
def get_organizations_by_building(
    building_id: int,
    db: Session = Depends(get_db),
) -> list[OrganizationResponse]:
    """Получить организации по ID здания."""
    service = OrganizationService(db)
    return service.get_organizations_by_building(building_id)


@router.get(
    "/by-activity/{activity_id}",
    response_model=list[OrganizationResponse],
    summary="Организации по виду деятельности",
    description="Получить список организаций по виду деятельности. "
                "При include_children=true включает организации с дочерними деятельностями.",
    responses={
        404: {"model": ErrorResponse, "description": "Activity not found"},
    },
)
def get_organizations_by_activity(
    activity_id: int,
    include_children: bool = Query(
        False,
        description="Включить организации с дочерними деятельностями",
    ),
    db: Session = Depends(get_db),
) -> list[OrganizationResponse]:
    """Получить организации по виду деятельности."""
    service = OrganizationService(db)
    return service.get_organizations_by_activity(activity_id, include_children)


@router.get(
    "/in-radius",
    response_model=list[OrganizationResponse],
    summary="Организации в радиусе от точки",
    description="Получить список организаций в заданном радиусе от указанной точки.",
)
def get_organizations_in_radius(
    latitude: float = Query(..., ge=-90, le=90, description="Широта центра"),
    longitude: float = Query(..., ge=-180, le=180, description="Долгота центра"),
    radius_km: float = Query(..., gt=0, le=1000, description="Радиус в километрах"),
    db: Session = Depends(get_db),
) -> list[OrganizationResponse]:
    """Получить организации в радиусе от точки."""
    service = OrganizationService(db)
    return service.get_organizations_in_radius(latitude, longitude, radius_km)


@router.get(
    "/in-box",
    response_model=list[OrganizationResponse],
    summary="Организации в прямоугольной области",
    description="Получить список организаций в прямоугольной географической области.",
)
def get_organizations_in_bounding_box(
    min_lat: float = Query(..., ge=-90, le=90, description="Минимальная широта"),
    max_lat: float = Query(..., ge=-90, le=90, description="Максимальная широта"),
    min_lon: float = Query(..., ge=-180, le=180, description="Минимальная долгота"),
    max_lon: float = Query(..., ge=-180, le=180, description="Максимальная долгота"),
    db: Session = Depends(get_db),
) -> list[OrganizationResponse]:
    """Получить организации в прямоугольной области."""
    service = OrganizationService(db)
    return service.get_organizations_in_box(min_lat, max_lat, min_lon, max_lon)


@router.get(
    "/{organization_id}",
    response_model=OrganizationResponse,
    summary="Получить организацию по ID",
    description="Получить полную информацию об организации, включая здание и деятельности.",
    responses={
        404: {"model": ErrorResponse, "description": "Organization not found"},
    },
)
def get_organization(
    organization_id: int,
    db: Session = Depends(get_db),
) -> OrganizationResponse:
    """Получить организацию по ID."""
    service = OrganizationService(db)
    return service.get_organization(organization_id)


@router.post(
    "/",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать организацию",
    description="Создать новую организацию с привязкой к зданию и деятельностям.",
    responses={
        400: {"model": ErrorResponse, "description": "Bad request"},
    },
)
def create_organization(
    org_data: OrganizationCreate,
    db: Session = Depends(get_db),
) -> OrganizationResponse:
    """Создать новую организацию."""
    service = OrganizationService(db)
    return service.create_organization(org_data)


@router.put(
    "/{organization_id}",
    response_model=OrganizationResponse,
    summary="Обновить организацию",
    responses={
        400: {"model": ErrorResponse, "description": "Bad request"},
        404: {"model": ErrorResponse, "description": "Organization not found"},
    },
)
def update_organization(
    organization_id: int,
    org_data: OrganizationUpdate,
    db: Session = Depends(get_db),
) -> OrganizationResponse:
    """Обновить существующую организацию."""
    service = OrganizationService(db)
    return service.update_organization(organization_id, org_data)
