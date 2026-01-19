from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories import (
    OrganizationRepository,
    BuildingRepository,
    ActivityRepository,
)
from app.schemas import OrganizationCreate, OrganizationUpdate
from app.models import Organization


class OrganizationService:
    """Сервис бизнес-логики для организаций."""

    def __init__(self, db: Session):
        self.db = db
        self.org_repo = OrganizationRepository(db)
        self.building_repo = BuildingRepository(db)
        self.activity_repo = ActivityRepository(db)

    def get_organization(self, org_id: int) -> Organization:
        """Получить организацию по ID с проверкой существования."""
        organization = self.org_repo.get_by_id(org_id)
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Organization with id {org_id} not found",
            )
        return organization

    def get_organizations_by_building(self, building_id: int) -> list[Organization]:
        """Получить организации по ID здания с проверкой существования здания."""
        building = self.building_repo.get_by_id(building_id)
        if not building:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Building with id {building_id} not found",
            )
        return self.org_repo.get_by_building_id(building_id)

    def get_organizations_by_activity(
        self, activity_id: int, include_children: bool = False
    ) -> list[Organization]:
        """
        Получить организации по виду деятельности.
        
        Args:
            activity_id: ID деятельности
            include_children: Если True, включает организации с дочерними деятельностями
        """
        activity = self.activity_repo.get_by_id(activity_id)
        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Activity with id {activity_id} not found",
            )
        
        if include_children:
            # Получаем все ID деятельностей в поддереве
            activity_ids = self.activity_repo.get_subtree_ids(activity_id)
            return self.org_repo.get_by_activity_ids(activity_ids)
        
        return self.org_repo.get_by_activity_id(activity_id)

    def get_organizations_in_radius(
        self, lat: float, lon: float, radius_km: float
    ) -> list[Organization]:
        """Получить организации в заданном радиусе от точки."""
        buildings = self.building_repo.get_in_radius(lat, lon, radius_km)
        building_ids = [b.id for b in buildings]
        return self.org_repo.get_by_building_ids(building_ids)

    def get_organizations_in_box(
        self, min_lat: float, max_lat: float, min_lon: float, max_lon: float
    ) -> list[Organization]:
        """Получить организации в прямоугольной области."""
        buildings = self.building_repo.get_in_bounding_box(
            min_lat, max_lat, min_lon, max_lon
        )
        building_ids = [b.id for b in buildings]
        return self.org_repo.get_by_building_ids(building_ids)

    def search_by_name(self, name: str) -> list[Organization]:
        """Поиск организаций по названию."""
        if len(name) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Search query must be at least 2 characters long",
            )
        return self.org_repo.search_by_name(name)

    def create_organization(self, org_data: OrganizationCreate) -> Organization:
        """Создать новую организацию с валидацией."""
        # Проверяем существование здания
        building = self.building_repo.get_by_id(org_data.building_id)
        if not building:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Building with id {org_data.building_id} not found",
            )
        
        # Проверяем существование деятельностей
        activities = []
        if org_data.activity_ids:
            activities = self.activity_repo.get_by_ids(org_data.activity_ids)
            if len(activities) != len(org_data.activity_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Some activity IDs are invalid",
                )
        
        return self.org_repo.create(org_data, activities)

    def update_organization(
        self, org_id: int, org_data: OrganizationUpdate
    ) -> Organization:
        """Обновить организацию с валидацией."""
        # Проверяем существование организации
        existing = self.org_repo.get_by_id(org_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Organization with id {org_id} not found",
            )
        
        # Проверяем здание если оно обновляется
        if org_data.building_id:
            building = self.building_repo.get_by_id(org_data.building_id)
            if not building:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Building with id {org_data.building_id} not found",
                )
        
        # Проверяем деятельности если они обновляются
        activities = None
        if org_data.activity_ids is not None:
            activities = self.activity_repo.get_by_ids(org_data.activity_ids)
            if len(activities) != len(org_data.activity_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Some activity IDs are invalid",
                )
        
        return self.org_repo.update(org_id, org_data, activities)
