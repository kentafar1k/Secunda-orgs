from sqlalchemy.orm import Session
from app.db.session import SessionLocal, Base, engine
from app.models import Building, Activity, Organization, Phone


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        if db.query(Building).count() > 0:
            return

        b1 = Building(address="г. Москва, ул. Ленина 1, офис 3", latitude=55.7558, longitude=37.6176)
        b2 = Building(address="г. Москва, ул. Тверская 10", latitude=55.7650, longitude=37.6050)
        db.add_all([b1, b2])
        db.flush()

        # Activities tree (max 3 levels)
        food = Activity(name="Еда")
        cars = Activity(name="Автомобили")
        db.add_all([food, cars])
        db.flush()

        meat = Activity(name="Мясная продукция", parent_id=food.id)
        dairy = Activity(name="Молочная продукция", parent_id=food.id)
        trucks = Activity(name="Грузовые", parent_id=cars.id)
        passenger = Activity(name="Легковые", parent_id=cars.id)
        db.add_all([meat, dairy, trucks, passenger])
        db.flush()

        parts = Activity(name="Запчасти", parent_id=passenger.id)
        accessories = Activity(name="Аксессуары", parent_id=passenger.id)
        db.add_all([parts, accessories])
        db.flush()

        org1 = Organization(name="ООО Рога и Копыта", building_id=b1.id)
        org1.activities.extend([meat, dairy])
        db.add(org1)
        db.flush()
        db.add_all([
            Phone(number="2-222-222", organization_id=org1.id),
            Phone(number="8-923-666-13-13", organization_id=org1.id),
        ])

        org2 = Organization(name="АвтоМир", building_id=b2.id)
        org2.activities.extend([parts, accessories])
        db.add(org2)
        db.flush()
        db.add(Phone(number="3-333-333", organization_id=org2.id))

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed()


