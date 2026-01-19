from sqlalchemy.orm import Session
from app.models import Activity
from app.schemas import ActivityCreate


class ActivityRepository:
    """Репозиторий для CRUD операций с деятельностями."""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Activity]:
        """Получить все деятельности."""
        return self.db.query(Activity).all()

    def get_by_id(self, activity_id: int) -> Activity | None:
        """Получить деятельность по ID."""
        return self.db.query(Activity).filter(Activity.id == activity_id).first()

    def get_root_activities(self) -> list[Activity]:
        """Получить корневые деятельности (без родителя)."""
        return self.db.query(Activity).filter(Activity.parent_id.is_(None)).all()

    def create(self, activity_data: ActivityCreate) -> Activity:
        """
        Создать новую деятельность.
        Автоматически рассчитывает уровень на основе родителя.
        """
        level = 1
        if activity_data.parent_id:
            parent = self.get_by_id(activity_data.parent_id)
            if parent:
                level = parent.level + 1
        
        activity = Activity(
            name=activity_data.name,
            parent_id=activity_data.parent_id,
            level=level,
        )
        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)
        return activity

    def get_subtree_ids(self, activity_id: int) -> list[int]:
        """
        Получить все ID деятельностей в поддереве (включая корневую).
        Используется для поиска организаций по деятельности с учетом дочерних.
        """
        result = [activity_id]
        
        # Рекурсивно собираем все дочерние деятельности
        children = self.db.query(Activity).filter(
            Activity.parent_id == activity_id
        ).all()
        
        for child in children:
            result.extend(self.get_subtree_ids(child.id))
        
        return result

    def get_by_ids(self, activity_ids: list[int]) -> list[Activity]:
        """Получить деятельности по списку ID."""
        if not activity_ids:
            return []
        return self.db.query(Activity).filter(
            Activity.id.in_(activity_ids)
        ).all()
