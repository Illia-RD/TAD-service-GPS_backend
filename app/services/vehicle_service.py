from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.equipment import FuelTank, LlsSensor
from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate


def get_all_vehicles(db: Session):
    return db.query(Vehicle).filter(Vehicle.deleted_at.is_(None)).all()


def get_vehicle_by_id(db: Session, vehicle_id: int):
    return (
        db.query(Vehicle)
        .filter(Vehicle.id == vehicle_id, Vehicle.deleted_at.is_(None))
        .first()
    )


def create_vehicle(db: Session, vehicle_in: VehicleCreate):
    # Відокремлюємо баки і датчики від основних даних авто
    vehicle_data = vehicle_in.model_dump(exclude={"tanks", "lls_sensors"})
    db_vehicle = Vehicle(**vehicle_data)

    db.add(db_vehicle)
    db.flush()  # Отримуємо ID авто (db_vehicle.id), але ще не робимо остаточний commit

    # Зберігаємо баки
    for tank_in in vehicle_in.tanks:
        db_tank = FuelTank(**tank_in.model_dump(), vehicle_id=db_vehicle.id)
        db.add(db_tank)

    # Зберігаємо датчики (LLS)
    for lls_in in vehicle_in.lls_sensors:
        db_lls = LlsSensor(**lls_in.model_dump(), vehicle_id=db_vehicle.id)
        db.add(db_lls)

    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle


def soft_delete_vehicle(db: Session, vehicle_id: int):
    db_vehicle = get_vehicle_by_id(db, vehicle_id)
    if not db_vehicle:
        return None

    db_vehicle.deleted_at = datetime.now(timezone.utc)

    # Автоматично знімаємо всі трекери при видаленні авто
    for tracker in db_vehicle.trackers:
        tracker.vehicle_id = None
        tracker.status = "used"

    db.commit()
    return db_vehicle
