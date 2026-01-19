"""
Роутер для работы с деятельностями.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core import get_db, verify_api_key
from app.repositories import ActivityRepository
from app.schemas import ActivityResponse, ActivityCreate, ErrorResponse

router = APIRouter(
    prefix="/activities",
    tags=["Activities"],
    dependencies=[Depends(verify_api_key)],
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
    },
)


@router.get(
    "/",
    response_model=list[ActivityResponse],
    summary="Получить список всех деятельностей",
    description="Возвращает плоский список всех видов деятельности.",
)
def get_all_activities(db: Session = Depends(get_db)) -> list[ActivityResponse]:
    """Получить список всех деятельностей."""
    repo = ActivityRepository(db)
    return repo.get_all()


@router.get(
    "/tree",
    response_model=list[ActivityResponse],
    summary="Получить корневые деятельности",
    description="Возвращает только корневые деятельности (level=1).",
)
def get_root_activities(db: Session = Depends(get_db)) -> list[ActivityResponse]:
    """Получить корневые деятельности (верхний уровень дерева)."""
    repo = ActivityRepository(db)
    return repo.get_root_activities()


@router.get(
    "/{activity_id}",
    response_model=ActivityResponse,
    summary="Получить деятельность по ID",
    responses={
        404: {"model": ErrorResponse, "description": "Activity not found"},
    },
)
def get_activity(activity_id: int, db: Session = Depends(get_db)) -> ActivityResponse:
    """Получить информацию о деятельности по её ID."""
    repo = ActivityRepository(db)
    activity = repo.get_by_id(activity_id)
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Activity with id {activity_id} not found",
        )
    return activity


@router.post(
    "/",
    response_model=ActivityResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новую деятельность",
    description="Создает новую деятельность. Максимальный уровень вложенности - 3.",
    responses={
        400: {"model": ErrorResponse, "description": "Bad request"},
    },
)
def create_activity(
    activity_data: ActivityCreate,
    db: Session = Depends(get_db),
) -> ActivityResponse:
    """
    Создать новую деятельность.
    Уровень вычисляется автоматически на основе родителя.
    """
    repo = ActivityRepository(db)
    
    # Проверяем родителя и уровень
    if activity_data.parent_id:
        parent = repo.get_by_id(activity_data.parent_id)
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Parent activity with id {activity_data.parent_id} not found",
            )
        # Проверка максимальной глубины (3 уровня)
        if parent.level >= 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum nesting level (3) exceeded. Cannot create 4th level activity.",
            )
    
    return repo.create(activity_data)
