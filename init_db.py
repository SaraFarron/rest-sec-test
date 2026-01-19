"""
Скрипт для инициализации базы данных тестовыми данными.
"""
from app.core.database import engine, SessionLocal, Base
from app.models.models import Building, Activity, Organization


def init_db():
    """Создание таблиц и заполнение тестовыми данными."""
    # Создаем таблицы
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Проверяем, есть ли уже данные
        if db.query(Building).first():
            print("Database already initialized")
            return
        
        # ==================== Здания ====================
        buildings = [
            Building(id=1, address="г. Москва, ул. Тверская, д. 1", latitude=55.7558, longitude=37.6173),
            Building(id=2, address="г. Москва, ул. Арбат, д. 10", latitude=55.7520, longitude=37.5920),
            Building(id=3, address="г. Москва, Ленинский проспект, д. 25", latitude=55.7100, longitude=37.5800),
            Building(id=4, address="г. Москва, ул. Новый Арбат, д. 15", latitude=55.7530, longitude=37.5850),
            Building(id=5, address="г. Москва, Кутузовский проспект, д. 32", latitude=55.7400, longitude=37.5500),
        ]
        db.add_all(buildings)
        db.commit()
        
        # ==================== Деятельности ====================
        # Уровень 1
        activities_l1 = [
            Activity(id=1, name="Еда", parent_id=None, level=1),
            Activity(id=2, name="Автомобили", parent_id=None, level=1),
            Activity(id=3, name="Услуги", parent_id=None, level=1),
            Activity(id=4, name="Медицина", parent_id=None, level=1),
        ]
        db.add_all(activities_l1)
        db.commit()
        
        # Уровень 2
        activities_l2 = [
            Activity(id=5, name="Мясная продукция", parent_id=1, level=2),
            Activity(id=6, name="Молочная продукция", parent_id=1, level=2),
            Activity(id=7, name="Выпечка", parent_id=1, level=2),
            Activity(id=8, name="Грузовые", parent_id=2, level=2),
            Activity(id=9, name="Легковые", parent_id=2, level=2),
            Activity(id=10, name="Ремонт техники", parent_id=3, level=2),
            Activity(id=11, name="Юридические услуги", parent_id=3, level=2),
            Activity(id=12, name="Стоматология", parent_id=4, level=2),
            Activity(id=13, name="Терапия", parent_id=4, level=2),
        ]
        db.add_all(activities_l2)
        db.commit()
        
        # Уровень 3
        activities_l3 = [
            Activity(id=14, name="Запчасти", parent_id=9, level=3),
            Activity(id=15, name="Аксессуары", parent_id=9, level=3),
            Activity(id=16, name="Шиномонтаж", parent_id=9, level=3),
            Activity(id=17, name="Ремонт телефонов", parent_id=10, level=3),
            Activity(id=18, name="Ремонт компьютеров", parent_id=10, level=3),
            Activity(id=19, name="Хлеб", parent_id=7, level=3),
            Activity(id=20, name="Кондитерские изделия", parent_id=7, level=3),
        ]
        db.add_all(activities_l3)
        db.commit()
        
        # ==================== Организации ====================
        organizations_data = [
            (1, 'ООО "Мясной Дом"', ["+7-495-111-1111", "+7-495-111-1112"], 1, [1, 5]),
            (2, 'АО "Молочный Рай"', ["+7-495-222-2222"], 1, [1, 6]),
            (3, 'ИП Иванов "АвтоЗапчасти"', ["+7-495-333-3333", "+7-495-333-3334"], 2, [2, 9, 14]),
            (4, 'ООО "Правовая Защита"', ["+7-495-444-4444"], 2, [3, 11]),
            (5, 'Клиника "Здоровая Улыбка"', ["+7-495-555-5555", "+7-495-555-5556"], 3, [4, 12]),
            (6, 'СТО "Грузовик Сервис"', ["+7-495-666-6666"], 3, [2, 8]),
            (7, 'Пекарня "Свежий Хлеб"', ["+7-495-777-7777"], 4, [1, 7, 19]),
            (8, 'Сервисный центр "ТехноМастер"', ["+7-495-888-8888", "+7-495-888-8889"], 4, [3, 10, 17, 18]),
            (9, 'Автосалон "Премиум Авто"', ["+7-495-999-9999"], 5, [2, 9, 15]),
            (10, 'Медицинский центр "Здоровье"', ["+7-495-000-0000", "+7-495-000-0001"], 5, [4, 12, 13]),
        ]
        
        for org_id, name, phones, building_id, activity_ids in organizations_data:
            org = Organization(
                id=org_id,
                name=name,
                building_id=building_id,
            )
            org.phone_numbers = phones
            
            # Добавляем деятельности
            activities = db.query(Activity).filter(Activity.id.in_(activity_ids)).all()
            org.activities = activities
            
            db.add(org)
        
        db.commit()
        print("Database initialized with test data!")
        
    except Exception as e:
        db.rollback()
        print(f"Error initializing database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
