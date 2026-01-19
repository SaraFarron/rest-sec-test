from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models import Building
from app.schemas import BuildingCreate


class BuildingRepository:
    """Репозиторий для CRUD операций со зданиями."""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Building]:
        """Получить все здания."""
        return self.db.query(Building).all()

    def get_by_id(self, building_id: int) -> Building | None:
        """Получить здание по ID."""
        return self.db.query(Building).filter(Building.id == building_id).first()

    def create(self, building_data: BuildingCreate) -> Building:
        """Создать новое здание."""
        building = Building(**building_data.model_dump())
        self.db.add(building)
        self.db.commit()
        self.db.refresh(building)
        return building

    def get_in_radius(
        self, lat: float, lon: float, radius_km: float
    ) -> list[Building]:
        """
        Получить здания в заданном радиусе от точки.
        Используем упрощенную формулу Хаверсина для небольших расстояний.
        1 градус широты ≈ 111 км, 1 градус долготы ≈ 111 * cos(lat) км
        """
        # Приблизительный расчет границ для предварительной фильтрации
        import math
        lat_delta = radius_km / 111.0
        lon_delta = radius_km / (111.0 * math.cos(math.radians(lat)))
        
        buildings = self.db.query(Building).filter(
            and_(
                Building.latitude >= lat - lat_delta,
                Building.latitude <= lat + lat_delta,
                Building.longitude >= lon - lon_delta,
                Building.longitude <= lon + lon_delta,
            )
        ).all()
        
        # Точная фильтрация по расстоянию
        result = []
        for building in buildings:
            distance = self._haversine_distance(
                lat, lon, building.latitude, building.longitude
            )
            if distance <= radius_km:
                result.append(building)
        return result

    def get_in_bounding_box(
        self, min_lat: float, max_lat: float, min_lon: float, max_lon: float
    ) -> list[Building]:
        """Получить здания в прямоугольной области."""
        return self.db.query(Building).filter(
            and_(
                Building.latitude >= min_lat,
                Building.latitude <= max_lat,
                Building.longitude >= min_lon,
                Building.longitude <= max_lon,
            )
        ).all()

    @staticmethod
    def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Расчет расстояния между двумя точками по формуле Хаверсина.
        Возвращает расстояние в километрах.
        """
        import math
        R = 6371  # Радиус Земли в км
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (
            math.sin(delta_lat / 2) ** 2 +
            math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
