from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.api.dependencies import DbSession
from app.models.tare import TarArchive
from app.models.vehicle import FuelTank
from app.schemas.tare import TarArchiveResponse, TarArchiveUpdate
from app.services.tare_parser import process_and_save_tare_file

router = APIRouter()
UPLOAD_DIR = "uploads/tare_files"


@router.get("/archive", response_model=list[TarArchiveResponse])
def get_tar_archives(db: DbSession):
    files = db.query(TarArchive).filter(TarArchive.deleted_at.is_(None)).all()
    # Спочатку закріплені, потім за датою створення
    return sorted(files, key=lambda x: (not x.is_favorite, x.created_at), reverse=True)


@router.post("/upload", response_model=TarArchiveResponse)
async def upload_archive_tare(
    db: DbSession,
    file: Annotated[UploadFile, File()],
    original_vehicle_number: Annotated[str | None, Form()] = None,
    nominal_volume: Annotated[float | None, Form()] = None,
    dim_l: Annotated[float | None, Form()] = None,
    dim_w: Annotated[float | None, Form()] = None,
    dim_h: Annotated[float | None, Form()] = None,
    h1: Annotated[float | None, Form()] = None,
    h2: Annotated[float | None, Form()] = None,
    no_neck_access: Annotated[bool, Form()] = False,
    is_favorite: Annotated[bool, Form()] = False,
    created_at: Annotated[str | None, Form()] = None,
):
    content_bytes = await file.read()

    # Зверни увагу: я використовую `_` для new_filename, щоб Pylance не сварився
    file_path, _ = process_and_save_tare_file(content_bytes, file.filename, UPLOAD_DIR)

    if not file_path:
        raise HTTPException(status_code=400, detail="Формат файлу не розпізнано!")

    # Генеруємо назву, якщо її немає
    default_name = f"{original_vehicle_number or 'Невідоме авто'} / {datetime.now().strftime('%d.%m.%Y')}"

    parsed_date = datetime.now(timezone.utc)
    if created_at:
        try:
            parsed_date = datetime.fromisoformat(created_at)
        except ValueError:
            pass

    db_file = TarArchive(
        file_name=default_name,
        original_vehicle_number=original_vehicle_number,
        file_path=file_path,
        is_favorite=is_favorite,
        nominal_volume=nominal_volume,
        dim_l=dim_l,
        dim_w=dim_w,
        dim_h=dim_h,
        h1=h1,
        h2=h2,
        no_neck_access=no_neck_access,
        created_at=parsed_date,
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file


@router.patch("/{tar_id}", response_model=TarArchiveResponse)
def update_tar_archive(tar_id: int, update_data: TarArchiveUpdate, db: DbSession):
    db_file = (
        db.query(TarArchive)
        .filter(TarArchive.id == tar_id, TarArchive.deleted_at.is_(None))
        .first()
    )
    if not db_file:
        raise HTTPException(status_code=404, detail="ТАР файл не знайдено")

    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(db_file, key, value)

    db.commit()
    db.refresh(db_file)
    return db_file


@router.delete("/{tar_id}")
def delete_tar_archive(tar_id: int, db: DbSession):
    db_file = db.query(TarArchive).filter(TarArchive.id == tar_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="ТАР файл не знайдено")

    db_file.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return {"message": "ТАР файл переміщено в корзину"}


@router.get("/{tar_id}/vehicles")
def get_vehicles_for_tar(tar_id: int, db: DbSession):
    # Шукаємо всі баки, до яких прив'язаний цей ТАР-файл
    tanks = db.query(FuelTank).filter(FuelTank.tar_archive_id == tar_id).all()

    result = []
    for tank in tanks:
        if tank.vehicle and not tank.vehicle.deleted_at:
            result.append(
                {
                    "vehicle_id": tank.vehicle.id,
                    "plate": tank.vehicle.plate,
                    "tank_id": tank.id,
                }
            )
    return result
