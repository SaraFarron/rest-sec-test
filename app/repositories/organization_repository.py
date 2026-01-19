"""
Репозиторий для работы с организациями.
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.models import Organization, Activity
from app.schemas import OrganizationCreate, OrganizationUpdate


class OrganizationRepository:
    """Репозиторий для CRUD операций с организациями."""

    def __init__(self, db: Session):
        self.db = db

    def _base_query(self):
        """Базовый запрос с подгрузкой связанных сущностей."""
        return self.db.query(Organization).options(
            joinedload(Organization.building),
            joinedload(Organization.activities),
        )

    def get_all(self) -> list[Organization]:
        """Получить все организации."""
        return self._base_query().all()

    def get_by_id(self, org_id: int) -> Organization | None:
        """Получить организацию по ID."""
        return self._base_query().filter(Organization.id == org_id).first()

    def get_by_building_id(self, building_id: int) -> list[Organization]:
        """Получить все организации в конкретном здании."""
        return self._base_query().filter(
            Organization.building_id == building_id
        ).all()

    def get_by_activity_id(self, activity_id: int) -> list[Organization]:
        """Получить организации по конкретному виду деятельности."""
        return self._base_query().filter(
            Organization.activities.any(Activity.id == activity_id)
        ).all()

    def get_by_activity_ids(self, activity_ids: list[int]) -> list[Organization]:
        """
        Получить организации по списку ID деятельностей.
        Используется для поиска с учетом поддерева деятельностей.
        """
        if not activity_ids:
            return []
        return self._base_query().filter(
            Organization.activities.any(Activity.id.in_(activity_ids))
        ).all()

    def get_by_building_ids(self, building_ids: list[int]) -> list[Organization]:
        """Получить организации по списку ID зданий."""
        if not building_ids:
            return []
        return self._base_query().filter(
            Organization.building_id.in_(building_ids)
        ).all()

    def search_by_name(self, name: str) -> list[Organization]:
        """
        Поиск организаций по названию (частичное совпадение, case-insensitive).
        """
        search_pattern = f"%{name}%"
        return self._base_query().filter(
            func.lower(Organization.name).like(func.lower(search_pattern))
        ).all()

    def create(
        self, org_data: OrganizationCreate, activities: list[Activity]
    ) -> Organization:
        """Создать новую организацию."""
        organization = Organization(
            name=org_data.name,
            phone_numbers=org_data.phone_numbers,
            building_id=org_data.building_id,
        )
        organization.activities = activities
        
        self.db.add(organization)
        self.db.commit()
        self.db.refresh(organization)
        return organization

    def update(
        self,
        org_id: int,
        org_data: OrganizationUpdate,
        activities: list[Activity] | None = None,
    ) -> Organization | None:
        """Обновить организацию."""
        organization = self.db.query(Organization).filter(
            Organization.id == org_id
        ).first()
        
        if not organization:
            return None
        
        update_data = org_data.model_dump(exclude_unset=True)
        
        # Убираем activity_ids из данных, т.к. это отдельная связь
        update_data.pop("activity_ids", None)
        
        for field, value in update_data.items():
            setattr(organization, field, value)
        
        if activities is not None:
            organization.activities = activities
        
        self.db.commit()
        self.db.refresh(organization)
        return organization

    def delete(self, org_id: int) -> bool:
        """Удалить организацию."""
        organization = self.db.query(Organization).filter(
            Organization.id == org_id
        ).first()
        
        if not organization:
            return False
        
        self.db.delete(organization)
        self.db.commit()
        return True
