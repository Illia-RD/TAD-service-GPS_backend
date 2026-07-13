from typing import List

from fastapi import APIRouter, Depends
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
