import json
from sqlalchemy import (
    Column, Integer, String, Float, ForeignKey, Table, CheckConstraint, Index, Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from app.core.database import Base


# Связующая таблица для M2M связи организаций и деятельностей
organization_activities = Table(
    "organization_activities",
    Base.metadata,
    Column(
        "organization_id",
        Integer,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "activity_id",
        Integer,
        ForeignKey("activities.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Building(Base):
    """
    Модель здания.
    Содержит адрес и географические координаты.
    """
    __tablename__ = "buildings"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String(500), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    # Связь с организациями (одно здание - много организаций)
    organizations = relationship("Organization", back_populates="building")

    # Индекс для геопоиска
    __table_args__ = (
        Index("idx_building_coordinates", "latitude", "longitude"),
    )


class Activity(Base):
    """
    Модель деятельности (иерархическая структура).
    Максимальная глубина вложенности - 3 уровня.
    """
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("activities.id", ondelete="CASCADE"), nullable=True)
    level = Column(Integer, nullable=False, default=1)

    # Самосвязь для древовидной структуры
    parent = relationship("Activity", remote_side=[id], back_populates="children")
    children = relationship("Activity", back_populates="parent", cascade="all, delete-orphan")

    # Связь с организациями через M2M
    organizations = relationship(
        "Organization",
        secondary=organization_activities,
        back_populates="activities",
    )

    __table_args__ = (
        # Ограничение: уровень от 1 до 3
        CheckConstraint("level >= 1 AND level <= 3", name="check_activity_level"),
        Index("idx_activity_parent", "parent_id"),
    )


class Organization(Base):
    """
    Модель организации.
    Связана с одним зданием и может иметь несколько видов деятельности.
    """
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(500), nullable=False, index=True)
    # Храним телефоны как JSON-строку (для совместимости с SQLite)
    _phone_numbers = Column("phone_numbers", Text, nullable=False)
    building_id = Column(
        Integer,
        ForeignKey("buildings.id", ondelete="RESTRICT"),
        nullable=False,
    )

    @hybrid_property
    def phone_numbers(self) -> list[str]:
        """Получить список телефонов."""
        if self._phone_numbers:
            return json.loads(self._phone_numbers)
        return []

    @phone_numbers.setter
    def phone_numbers(self, value: list[str]):
        """Установить список телефонов."""
        self._phone_numbers = json.dumps(value)

    # Связь с зданием
    building = relationship("Building", back_populates="organizations")

    # Связь с деятельностями (M2M)
    activities = relationship(
        "Activity",
        secondary=organization_activities,
        back_populates="organizations",
    )

    __table_args__ = (
        Index("idx_organization_building", "building_id"),
        Index("idx_organization_name_lower", "name"),  # Для поиска по названию
    )
