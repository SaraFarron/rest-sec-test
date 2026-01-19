"""
Роутер для работы со зданиями.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core import get_db, verify_api_key
from app.repositories import BuildingRepository
from app.schemas import BuildingResponse, BuildingCreate, ErrorResponse

router = APIRouter(
    prefix="/buildings",
    tags=["Buildings"],
    dependencies=[Depends(verify_api_key)],
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
    },
)


@router.get(
    "/",
    response_model=list[BuildingResponse],
    summary="Получить список всех зданий",
    description="Возвращает список всех зданий с их адресами и координатами.",
)
def get_all_buildings(db: Session = Depends(get_db)) -> list[BuildingResponse]:
    """Получить список всех зданий."""
    repo = BuildingRepository(db)
    return repo.get_all()


@router.get(
    "/{building_id}",
    response_model=BuildingResponse,
    summary="Получить здание по ID",
    responses={
        404: {"model": ErrorResponse, "description": "Building not found"},
    },
)
def get_building(building_id: int, db: Session = Depends(get_db)) -> BuildingResponse:
    """Получить информацию о здании по его ID."""
    repo = BuildingRepository(db)
    building = repo.get_by_id(building_id)
    if not building:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Building with id {building_id} not found",
        )
    return building


@router.post(
    "/",
    response_model=BuildingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новое здание",
)
def create_building(
    building_data: BuildingCreate,
    db: Session = Depends(get_db),
) -> BuildingResponse:
    """Создать новое здание."""
    repo = BuildingRepository(db)
    return repo.create(building_data)
