from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# Імпортуємо наші розбиті модулі
from app.api.deps import get_db
from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleResponse

# Створюємо роутер для авто
router = APIRouter()


# --- НОВИЙ ЕНДПОІНТ ДЛЯ ОТРИМАННЯ УНІКАЛЬНОГО ОБЛАДНАННЯ ---
@router.get("/other-equipment/unique")
def get_unique_other_equipment(db: Session = Depends(get_db)):  # noqa: B008
    """Отримати список унікальних значень додаткового обладнання з усіх авто"""
    vehicles = (
        db.query(Vehicle.other_equipment)
        .filter(Vehicle.other_equipment.isnot(None))
        .all()
    )

    unique_items = set()
    for (eq_string,) in vehicles:
        if eq_string:
            items = [item.strip() for item in eq_string.split(",") if item.strip()]
            unique_items.update(items)

    return [{"name": item} for item in sorted(unique_items)]


@router.get("/", response_model=list[VehicleResponse])
def get_vehicles(db: Session = Depends(get_db)):  # noqa: B008
    """Отримати список усіх транспортних засобів"""
    return db.query(Vehicle).all()


@router.post("/")
def create_vehicle(vehicle: VehicleCreate, db: Session = Depends(get_db)):  # noqa: B008
    db_vehicle = Vehicle(**vehicle.model_dump())
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle
    

# --- ЕНДПОІНТ ОНОВЛЕННЯ ---
@router.put("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(
    vehicle_id: int,
    vehicle: VehicleCreate,
    db: Session = Depends(get_db),  # noqa: B008
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
