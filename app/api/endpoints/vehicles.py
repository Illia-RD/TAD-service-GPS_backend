import os
import shutil
from datetime import datetime, timezone, timedelta
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

# Імпортуємо наші розбиті модулі
from app.api.deps import get_db
from app.models.vehicle import Vehicle, VehicleFile

# === ОСЬ ТУТ ТЕПЕР ПРАВИЛЬНИЙ ІМПОРТ ВСІХ СХЕМ ===
from app.schemas.vehicle import (
    VehicleCreate,
    VehicleResponse,
    VehicleFileResponse,
    VehicleFileUpdate,
)
from app.services.tare_parser import process_and_save_tare_file

# Створюємо роутер для авто
router = APIRouter()

# Шлях для збереження файлів тарування
UPLOAD_DIR = "uploads/tare_files"


# 1. Функція автоочищення
def cleanup_old_trash(db: Session):
    # ДЛЯ ТЕСТІВ: 5 хвилин. Коли перевіриш, заміниш minutes=5 на days=30
    expiration_date = datetime.now(timezone.utc) - timedelta(minutes=5)

    # Видаляємо прострочені файли
    old_files = (
        db.query(VehicleFile)
        .filter(
            VehicleFile.deleted_at != None, VehicleFile.deleted_at < expiration_date
        )
        .all()
    )
    for f in old_files:
        if os.path.exists(f.file_path):
            os.remove(f.file_path)
        db.delete(f)

    # Видаляємо прострочені авто
    old_vehicles = (
        db.query(Vehicle)
        .filter(Vehicle.deleted_at != None, Vehicle.deleted_at < expiration_date)
        .all()
    )
    for v in old_vehicles:
        for f in v.files:  # Зносимо і всі їхні фізичні файли з диска
            if os.path.exists(f.file_path):
                os.remove(f.file_path)
        db.delete(v)

    db.commit()


# 2. ЕНДПОІНТ КОРЗИНИ (МАЄ БУТИ ВИЩЕ ІНШИХ GET/POST З {vehicle_id})
@router.get("/trash/")
def get_trash(db: Session = Depends(get_db)):  # noqa: B008
    # 1. Спершу чистимо те, що лежить довше 5 хвилин
    cleanup_old_trash(db)

    # 2. Дістаємо те, що залишилося в корзині
    deleted_vehicles = db.query(Vehicle).filter(Vehicle.deleted_at != None).all()
    deleted_files = db.query(VehicleFile).filter(VehicleFile.deleted_at != None).all()

    vehicles_data = [
        {
            "id": v.id,
            "title": f"#{v.internal_id} | {v.plate} ({v.make} {v.model})",
            "deleted_at": v.deleted_at,
        }
        for v in deleted_vehicles
    ]

    files_data = []
    for f in deleted_files:
        # Шукаємо авто, якому належав файл, щоб вивести це на екран
        vehicle = db.query(Vehicle).filter(Vehicle.id == f.vehicle_id).first()
        v_title = (
            f"#{vehicle.internal_id} | {vehicle.plate}" if vehicle else "Видалене авто"
        )
        files_data.append(
            {
                "id": f.id,
                "file_name": f.file_name,
                "vehicle_title": v_title,
                "deleted_at": f.deleted_at,
            }
        )

    return {"vehicles": vehicles_data, "files": files_data}


# 3. ЕНДПОІНТИ ДЛЯ ВІДНОВЛЕННЯ З КОРЗИНИ
@router.post("/{vehicle_id}/restore/")
def restore_vehicle(vehicle_id: int, db: Session = Depends(get_db)):  # noqa: B008
    v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if v:
        v.deleted_at = None
        db.commit()
    return {"message": "Авто відновлено"}


@router.post("/files/{file_id}/restore/")
def restore_file(file_id: int, db: Session = Depends(get_db)):  # noqa: B008
    f = db.query(VehicleFile).filter(VehicleFile.id == file_id).first()
    if f:
        f.deleted_at = None
        db.commit()
    return {"message": "Файл відновлено"}


# --- ОНОВЛЕНИЙ ЕНДПОІНТ ДЛЯ ЗАВАНТАЖЕННЯ ФАЙЛІВ З ПРИВ'ЯЗКОЮ ТА ПАРСИНГОМ ---
@router.post("/{vehicle_id}/upload-tare/")
async def upload_tare_file(
    vehicle_id: int,
    file: Annotated[UploadFile, File()],
    db: Annotated[Session, Depends(get_db)],
    tank_index: Annotated[int | None, Form()] = None,
    file_type: Annotated[str, Form()] = "тарування",
    no_neck_access: Annotated[bool, Form()] = False,
):
    # 1. Перевіряємо, чи існує авто
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Транспортний засіб не знайдено")

    # 2. Читаємо вміст файлу
    content_bytes = await file.read()
    try:
        raw_content = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raw_content = content_bytes.decode("cp1251", errors="ignore")

    # 3. Віддаємо парсеру
    file_path, new_filename = process_and_save_tare_file(
        raw_content, file.filename, UPLOAD_DIR
    )

    if not file_path:
        raise HTTPException(
            status_code=400,
            detail="❌ Формат файлу не розпізнано! Підтримуються: Igla 3D, Navitrack, Epsilon або CSV.",
        )

    # 4. Записуємо інформацію про файл у БД
    db_file = VehicleFile(
        vehicle_id=vehicle_id,
        file_name=new_filename,
        file_path=file_path,
        tank_index=tank_index,
        file_type=file_type,
        h1=None,
        h2=None,
        no_neck_access=no_neck_access,
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)

    # ПОВЕРНУВ ТВІЙ ДОВГИЙ СЛОВНИК НА МІСЦЕ
    return {
        "message": "Файл успішно завантажено та конвертовано в CSV",
        "id": db_file.id,
        "file_name": db_file.file_name,
        "file_path": db_file.file_path,
        "tank_index": db_file.tank_index,
        "file_type": db_file.file_type,
        "h1": db_file.h1,
        "h2": db_file.h2,
        "no_neck_access": db_file.no_neck_access,
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
    """Отримати список усіх транспортних засобів (які не в корзині)"""
    return db.query(Vehicle).filter(Vehicle.deleted_at.is_(None)).all()


@router.post("/")
def create_vehicle(vehicle: VehicleCreate, db: Session = Depends(get_db)):  # noqa: B008
    db_vehicle = Vehicle(**vehicle.model_dump())
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle


# --- ЕНДПОІНТ ОНОВЛЕННЯ ---
@router.put("/{vehicle_id}", response_model=VehicleResponse)
@router.put("/{vehicle_id}/", response_model=VehicleResponse)
def update_vehicle(
    vehicle_id: int,
    vehicle: VehicleCreate,
    db: Annotated[Session, Depends(get_db)],
):
    db_vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not db_vehicle:
        raise HTTPException(status_code=404, detail="Транспортний засіб не знайдено")

    for key, value in vehicle.model_dump().items():
        setattr(db_vehicle, key, value)

    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle


# --- НОВИЙ ЕНДПОІНТ: ОНОВЛЕННЯ H1, H2 ТА ГАЛОЧКИ ДЛЯ ФАЙЛУ ---
@router.put("/files/{file_id}/", response_model=VehicleFileResponse)
def update_tare_file(
    file_id: int, file_data: VehicleFileUpdate, db: Annotated[Session, Depends(get_db)]
):
    db_file = db.query(VehicleFile).filter(VehicleFile.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="Файл не знайдено")

    if file_data.h1 is not None:
        db_file.h1 = file_data.h1
    if file_data.h2 is not None:
        db_file.h2 = file_data.h2
    if file_data.no_neck_access is not None:
        db_file.no_neck_access = file_data.no_neck_access

    db.commit()
    db.refresh(db_file)
    return db_file


@router.delete("/{vehicle_id}")
def delete_vehicle(vehicle_id: int, db: Session = Depends(get_db)):  # noqa: B008
    db_vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not db_vehicle:
        raise HTTPException(status_code=404, detail="Транспортний засіб не знайдено")

    # Замість db.delete(db_vehicle) ми просто ставимо дату видалення!
    db_vehicle.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return {"message": "Автомобіль переміщено в корзину"}


# 3. ОНОВЛЕНИЙ ЕНДПОІНТ: Видалення файлу (тепер теж йде в корзину!)
@router.delete("/files/{file_id}")
def delete_tare_file(file_id: int, db: Session = Depends(get_db)):  # noqa: B008
    db_file = db.query(VehicleFile).filter(VehicleFile.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="Файл не знайдено")

    # Ми БІЛЬШЕ НЕ ВИДАЛЯЄМО фізичний файл через os.remove() одразу!
    # Ставимо дату видалення
    db_file.deleted_at = datetime.now(timezone.utc)
    db.commit()

    return {"message": "Файл переміщено в корзину"}
