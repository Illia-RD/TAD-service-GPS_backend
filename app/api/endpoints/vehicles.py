from typing import List

# Додаємо HTTPException для обробки помилок
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# Імпортуємо наші розбиті модулі
from app.api.deps import get_db
from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleSchema

# Створюємо роутер для авто
router = APIRouter()


@router.get("/", response_model=List[VehicleSchema])
def get_vehicles(db: Session = Depends(get_db)):
    """Отримати список усіх транспортних засобів"""
    return db.query(Vehicle).all()


@router.post("/")
def create_vehicle(vehicle: VehicleCreate, db: Session = Depends(get_db)):
    db_vehicle = Vehicle(**vehicle.model_dump())
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle


# --- ДОДАЄМО ЕНДПОІНТ ОНОВЛЕННЯ ---
@router.put("/{vehicle_id}", response_model=VehicleSchema)
def update_vehicle(
    vehicle_id: int, vehicle: VehicleCreate, db: Session = Depends(get_db)
):
    # 1. Шукаємо авто в базі
    db_vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()

    # 2. Якщо такого немає - віддаємо помилку 404
    if not db_vehicle:
        raise HTTPException(status_code=404, detail="Транспортний засіб не знайдено")

    # 3. Оновлюємо всі поля, які прийшли з фронтенду
    for key, value in vehicle.model_dump().items():
        setattr(db_vehicle, key, value)

    # 4. Зберігаємо зміни
    db.commit()
    db.refresh(db_vehicle)

    return db_vehicle
