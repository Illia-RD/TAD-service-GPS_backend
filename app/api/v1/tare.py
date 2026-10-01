import os
from datetime import datetime, timezone
from pathlib import Path
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

    # file_path матиме вигляд типу "uploads/tare_files/6ca840f5_nazva.csv"
    file_path, _ = process_and_save_tare_file(content_bytes, file.filename, UPLOAD_DIR)

    if not file_path:
        raise HTTPException(status_code=400, detail="Формат файлу не розпізнано!")

    # Витягуємо чисту назву без розширення .csv (напр. "ВХ 8654 ІС_standart")
    clean_file_name = Path(file.filename).stem

    parsed_date = datetime.now(timezone.utc)
    if created_at:
        try:
            parsed_date = datetime.fromisoformat(created_at)
        except ValueError:
            pass

    db_file = TarArchive(
        file_name=clean_file_name,  # <--- Записуємо оригінальну назву
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

    # --- ЛОГІКА ПЕРЕЙМЕНУВАННЯ ФІЗИЧНОГО ФАЙЛУ ---
    if "file_name" in update_dict and update_dict["file_name"] != db_file.file_name:
        new_clean_name = update_dict["file_name"]
        old_path = Path(db_file.file_path)

        if old_path.exists():
            old_filename = old_path.name
            # Розділяємо по першому '_', щоб відділити UUID (якщо він є)
            parts = old_filename.split("_", 1)

            # Якщо є UUID на початку (напр. 6ca840f5), зберігаємо його
            if len(parts) == 2 and len(parts[0]) >= 8:
                prefix = parts[0]
                new_filename = f"{prefix}_{new_clean_name}.csv"
            else:
                new_filename = f"{new_clean_name}.csv"

            new_path = old_path.parent / new_filename

            try:
                os.rename(old_path, new_path)
                update_dict["file_path"] = str(new_path)  # Оновлюємо шлях для БД
            except OSError as e:
                print(f"Помилка перейменування файлу на диску: {e}")
                # Якщо не змогли перейменувати фізично - краще залишити як є,
                # щоб не втратити доступ до файлу

    # Застосовуємо всі оновлення до моделі
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
