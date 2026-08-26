import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.vehicle import Vehicle, VehicleFile
from app.schemas.vehicle import (
    VehicleCreate,
    VehicleFileResponse,
    VehicleFileUpdate,
    VehicleResponse,
)
from app.services.image_service import compress_and_save_photo
from app.services.tare_parser import process_and_save_tare_file

router = APIRouter()
DbSession = Annotated[Session, Depends(get_db)]
UPLOAD_DIR = "uploads/tare_files"


def cleanup_old_trash(db: Session):
    expiration_date = datetime.now(timezone.utc) - timedelta(minutes=5)

    old_files = (
        db.query(VehicleFile)
        .filter(
            VehicleFile.deleted_at.isnot(None), VehicleFile.deleted_at < expiration_date
        )
        .all()
    )
    for f in old_files:
        if os.path.exists(f.file_path):
            os.remove(f.file_path)
        db.delete(f)

    old_vehicles = (
        db.query(Vehicle)
        .filter(Vehicle.deleted_at.isnot(None), Vehicle.deleted_at < expiration_date)
        .all()
    )
    for v in old_vehicles:
        for f in v.files:
            if os.path.exists(f.file_path):
                os.remove(f.file_path)
        db.delete(v)
    db.commit()


@router.get("/trash/")
def get_trash(db: DbSession):
    cleanup_old_trash(db)
    deleted_vehicles = db.query(Vehicle).filter(Vehicle.deleted_at.isnot(None)).all()
    deleted_files = (
        db.query(VehicleFile).filter(VehicleFile.deleted_at.isnot(None)).all()
    )

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


@router.post("/{vehicle_id}/restore/")
def restore_vehicle(vehicle_id: int, db: DbSession):
    v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if v:
        v.deleted_at = None
        db.commit()
    return {"message": "Авто відновлено"}


@router.post("/files/{file_id}/restore/")
def restore_file(file_id: int, db: DbSession):
    f = db.query(VehicleFile).filter(VehicleFile.id == file_id).first()
    if f:
        f.deleted_at = None
        db.commit()
    return {"message": "Файл відновлено"}


@router.get("/archive/files/", response_model=list[VehicleFileResponse])
def get_archive_files(db: DbSession):
    """Отримати всі файли для Архіву, окрім видалених"""
    return db.query(VehicleFile).filter(VehicleFile.deleted_at.is_(None)).all()


@router.post("/upload/photo")
async def upload_tank_photo(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Файл має бути зображенням")

    try:
        contents = await file.read()
        photo_path = await compress_and_save_photo(contents)
        return {"photo_path": photo_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка обробки фото: {e!s}")


@router.post("/{vehicle_id}/upload-tare/")
async def upload_tare_file(
    vehicle_id: int,
    file: Annotated[UploadFile, File()],
    db: DbSession,
    tank_index: Annotated[int | None, Form()] = None,
    file_type: Annotated[str, Form()] = "тарування",
    no_neck_access: Annotated[bool, Form()] = False,
):
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Транспортний засіб не знайдено")

    content_bytes = await file.read()
    try:
        raw_content = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raw_content = content_bytes.decode("cp1251", errors="ignore")

    file_path, new_filename = process_and_save_tare_file(
        raw_content, file.filename, UPLOAD_DIR
    )
    if not file_path:
        raise HTTPException(
            status_code=400,
            detail="❌ Формат файлу не розпізнано! Підтримуються: Igla 3D, Navitrack, Epsilon або CSV.",
        )

    db_file = VehicleFile(
        vehicle_id=vehicle_id,
        file_name=new_filename,
        file_path=file_path,
        tank_index=tank_index,
        file_type=file_type,
        no_neck_access=no_neck_access,
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)

    return {
        "message": "Файл успішно завантажено",
        "id": db_file.id,
        "file_name": db_file.file_name,
        "file_path": db_file.file_path,
        "tank_index": db_file.tank_index,
        "file_type": db_file.file_type,
        "h1": db_file.h1,
        "h2": db_file.h2,
        "no_neck_access": db_file.no_neck_access,
    }


@router.get("/other-equipment/unique")
def get_unique_other_equipment(db: DbSession):
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
def get_vehicles(db: DbSession):
    return db.query(Vehicle).filter(Vehicle.deleted_at.is_(None)).all()


@router.post("/")
def create_vehicle(vehicle: VehicleCreate, db: DbSession):
    db_vehicle = Vehicle(**vehicle.model_dump())
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle


@router.put("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(vehicle_id: int, vehicle: VehicleCreate, db: DbSession):
    db_vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not db_vehicle:
        raise HTTPException(status_code=404, detail="Транспортний засіб не знайдено")

    for key, value in vehicle.model_dump().items():
        setattr(db_vehicle, key, value)

    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle


@router.put("/files/{file_id}/", response_model=VehicleFileResponse)
def update_tare_file(file_id: int, file_data: VehicleFileUpdate, db: DbSession):
    db_file = db.query(VehicleFile).filter(VehicleFile.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="Файл не знайдено")

    update_data = file_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_file, key, value)

    db.commit()
    db.refresh(db_file)
    return db_file


@router.delete("/{vehicle_id}")
def delete_vehicle(vehicle_id: int, db: DbSession):
    db_vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not db_vehicle:
        raise HTTPException(status_code=404, detail="Транспортний засіб не знайдено")
    db_vehicle.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return {"message": "Автомобіль переміщено в корзину"}


@router.delete("/files/{file_id}")
def delete_tare_file(file_id: int, db: DbSession):
    db_file = db.query(VehicleFile).filter(VehicleFile.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="Файл не знайдено")
    db_file.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return {"message": "Файл переміщено в корзину"}
