import os
import shutil
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

# Імпортуємо наші розбиті модулі
from app.api.deps import get_db
from app.models.vehicle import Vehicle, VehicleFile  # <--- Додали імпорт VehicleFile
from app.schemas.vehicle import VehicleCreate, VehicleResponse

# Створюємо роутер для авто
router = APIRouter()

# Шлях для збереження файлів тарування
UPLOAD_DIR = "uploads/tare_files"


# --- НОВИЙ ЕНДПОІНТ ДЛЯ ЗАВАНТАЖЕННЯ ТАРУВАЛЬНИХ ТАБЛИЦЬ ---
@router.post("/{vehicle_id}/upload-tare/")
def upload_tare_file(
    vehicle_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),  # noqa: B008
):
    # 1. Перевіряємо, чи існує авто
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Транспортний засіб не знайдено")

    # 2. Генеруємо унікальне ім'я файлу (щоб файли з однаковими іменами не перезаписувались)
    file_extension = file.filename.split(".")[-1] if "." in file.filename else "file"
    unique_filename = f"{vehicle_id}_{uuid4().hex[:8]}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # 3. Зберігаємо фізичний файл на диск
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 4. Записуємо інформацію про файл у БД
    db_file = VehicleFile(
        vehicle_id=vehicle_id,
        file_name=file.filename,
        file_path=file_path.replace("\\", "/"),  # Нормалізуємо скісні риски для URL
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)

    return {
        "message": "Файл успішно завантажено",
        "file_id": db_file.id,
        "file_name": db_file.file_name,
        "file_path": db_file.file_path,
    }


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


@router.delete("/files/{file_id}")
def delete_tare_file(file_id: int, db: Session = Depends(get_db)):  # noqa: B008
    # 1. Шукаємо файл у базі
    db_file = db.query(VehicleFile).filter(VehicleFile.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="Файл не знайдено")

    # 2. Видаляємо фізичний файл із папки uploads (якщо він там є)
    if os.path.exists(db_file.file_path):
        os.remove(db_file.file_path)

    # 3. Видаляємо запис із бази даних
    db.delete(db_file)
    db.commit()

    return {"message": "Файл успішно видалено"}
