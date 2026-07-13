from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

# Імпортуємо наші розбиті модулі
from app.api.deps import get_db
from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleSchema

# Створюємо роутер для авто
router = APIRouter()

@router.get("/", response_model=List[VehicleSchema])
def get_vehicles(db: Session = Depends(get_db)):
    """Отримати список усіх транспортних засобів"""
    return db.query(Vehicle).all()