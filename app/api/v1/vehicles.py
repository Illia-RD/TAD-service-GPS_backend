from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.api.dependencies import DbSession
from app.models.equipment import VehicleFile
from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleResponse
from app.services import vehicle_service
from app.services.image_service import compress_and_save_photo
from app.services.tare_parser import process_and_save_tare_file

router = APIRouter()
UPLOAD_DIR = "uploads/tare_files"


@router.get("/", response_model=list[VehicleResponse])
def get_vehicles(db: DbSession):
    return vehicle_service.get_all_vehicles(db)


@router.post("/", response_model=VehicleResponse)
def create_vehicle(vehicle_in: VehicleCreate, db: DbSession):
    return vehicle_service.create_vehicle(db, vehicle_in)


@router.delete("/{vehicle_id}")
def delete_vehicle(vehicle_id: int, db: DbSession):
    db_vehicle = vehicle_service.soft_delete_vehicle(db, vehicle_id)
    if not db_vehicle:
        raise HTTPException(status_code=404, detail="Транспортний засіб не знайдено")
    return {"message": "Автомобіль переміщено в корзину"}


# --- ФОТО ТА ТАРУВАННЯ ---


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
    db: DbSession,
    file: Annotated[UploadFile, File()],
    tank_index: Annotated[int | None, Form()] = None,
    file_type: Annotated[str, Form()] = "тарування",
    no_neck_access: Annotated[bool, Form()] = False,
):
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Авто не знайдено")

    content_bytes = await file.read()
    file_path, new_filename = process_and_save_tare_file(
        content_bytes, file.filename, UPLOAD_DIR
    )

    if not file_path:
        raise HTTPException(status_code=400, detail="Формат файлу не розпізнано!")

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
    return db_file


@router.delete("/files/{file_id}")
def delete_tare_file(file_id: int, db: DbSession):
    db_file = db.query(VehicleFile).filter(VehicleFile.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="Файл не знайдено")
    db_file.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return {"message": "Файл переміщено в корзину"}
