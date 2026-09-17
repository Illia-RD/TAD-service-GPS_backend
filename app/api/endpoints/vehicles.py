from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.vehicle import EquipmentLog, SimCard, Tracker, Vehicle, VehicleFile
from app.schemas.vehicle import (
    EquipmentLogResponse,
    SimCardBase,
    SimCardResponse,
    TrackerBase,
    TrackerResponse,
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


# === ХЕЛПЕР ДЛЯ ЛОГІЮВАННЯ РУХУ ОБЛАДНАННЯ ===
def log_equipment_action(
    db: Session,
    entity_type: str,
    entity_id: int,
    action: str,
    description: str,
    vehicle_id: int = None,
):
    log_entry = EquipmentLog(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        description=description,
        vehicle_id=vehicle_id,
    )
    db.add(log_entry)
    db.commit()


# === 1. АРХІВ ТА РЕЄСТР (4 ВКЛАДКИ) ===


@router.get("/archive/files/", response_model=list[VehicleFileResponse])
def get_archive_files(db: DbSession):
    """Вкладка 1: Архів файлів (всі файли, включаючи відв'язані)"""
    return db.query(VehicleFile).all()


@router.get("/archive/tanks/")
def get_archive_tanks(db: DbSession):
    """Вкладка 2: Реєстр усіх баків (витягуємо з JSON усіх автомобілів)"""
    vehicles = db.query(Vehicle).all()
    all_tanks = []
    for v in vehicles:
        if v.tanks_data:
            for tank in v.tanks_data:
                tank_info = tank.copy()
                tank_info["vehicle_plate"] = v.plate
                tank_info["vehicle_internal_id"] = v.internal_id
                all_tanks.append(tank_info)
    return all_tanks


@router.get("/archive/trackers/", response_model=list[TrackerResponse])
def get_archive_trackers(db: DbSession):
    """Вкладка 3: Склад усіх трекерів"""
    return db.query(Tracker).all()


@router.get("/archive/sim-cards/", response_model=list[SimCardResponse])
def get_archive_sims(db: DbSession):
    """Вкладка 4: Склад усіх сім-карт"""
    return db.query(SimCard).all()


@router.get("/archive/logs/", response_model=list[EquipmentLogResponse])
def get_equipment_logs(db: DbSession):
    """Історія руху всього обладнання"""
    return db.query(EquipmentLog).order_by(EquipmentLog.created_at.desc()).all()


# === 2. КЕРУВАННЯ ТРЕКЕРАМИ ===


@router.post("/trackers/", response_model=TrackerResponse)
def create_tracker(tracker: TrackerBase, db: DbSession):
    db_tracker = Tracker(**tracker.model_dump())
    db.add(db_tracker)
    db.commit()
    db.refresh(db_tracker)
    log_equipment_action(
        db,
        "tracker",
        db_tracker.id,
        "created",
        f"Трекер {db_tracker.imei} додано на склад",
    )
    return db_tracker


@router.post("/trackers/{tracker_id}/assign/{vehicle_id}")
def assign_tracker(tracker_id: int, vehicle_id: int, db: DbSession):
    tracker = db.query(Tracker).filter(Tracker.id == tracker_id).first()
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()

    if not tracker or not vehicle:
        raise HTTPException(status_code=404, detail="Трекер або авто не знайдено")

    tracker.vehicle_id = vehicle.id
    db.commit()
    log_equipment_action(
        db,
        "tracker",
        tracker.id,
        "installed",
        f"Трекер {tracker.imei} встановлено на авто {vehicle.plate}",
        vehicle.id,
    )
    return {"message": "Трекер успішно прив'язано до авто"}


@router.post("/trackers/{tracker_id}/remove")
def remove_tracker(tracker_id: int, db: DbSession):
    tracker = db.query(Tracker).filter(Tracker.id == tracker_id).first()
    if not tracker:
        raise HTTPException(status_code=404, detail="Трекер не знайдено")

    old_vehicle_id = tracker.vehicle_id
    tracker.vehicle_id = None
    tracker.status = "used"  # Змінюємо статус на вживаний після зняття
    db.commit()

    log_equipment_action(
        db,
        "tracker",
        tracker.id,
        "removed",
        f"Трекер {tracker.imei} знято з авто",
        old_vehicle_id,
    )
    return {"message": "Трекер знято з авто та переміщено на склад"}


# === 3. КЕРУВАННЯ СІМ-КАРТАМИ ===


@router.post("/sim-cards/", response_model=SimCardResponse)
def create_sim_card(sim: SimCardBase, db: DbSession):
    db_sim = SimCard(**sim.model_dump())
    db.add(db_sim)
    db.commit()
    db.refresh(db_sim)
    log_equipment_action(
        db,
        "sim",
        db_sim.id,
        "created",
        f"Сім-карту {db_sim.phone_number} додано на склад",
    )
    return db_sim


@router.post("/sim-cards/{sim_id}/assign/{tracker_id}")
def assign_sim_card(sim_id: int, tracker_id: int, db: DbSession):
    sim = db.query(SimCard).filter(SimCard.id == sim_id).first()
    tracker = db.query(Tracker).filter(Tracker.id == tracker_id).first()

    if not sim or not tracker:
        raise HTTPException(status_code=404, detail="Сім-карту або трекер не знайдено")

    sim.tracker_id = tracker.id
    sim.status = "active"
    db.commit()
    log_equipment_action(
        db,
        "sim",
        sim.id,
        "installed",
        f"Сімку {sim.phone_number} вставлено в трекер {tracker.imei}",
    )
    return {"message": "Сім-карту прив'язано до трекера"}


# === 4. КЕРУВАННЯ АВТОМОБІЛЯМИ (СТАНДАРТНИЙ CRUD) ===


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


@router.delete("/{vehicle_id}")
def delete_vehicle(vehicle_id: int, db: DbSession):
    db_vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not db_vehicle:
        raise HTTPException(status_code=404, detail="Транспортний засіб не знайдено")

    # При видаленні авто знімаємо всі трекери в резерв!
    for tracker in db_vehicle.trackers:
        tracker.vehicle_id = None
        log_equipment_action(
            db,
            "tracker",
            tracker.id,
            "removed",
            f"Автоматично знято через видалення авто {db_vehicle.plate}",
            vehicle_id,
        )

    db_vehicle.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return {"message": "Автомобіль переміщено в корзину"}


# === 5. КЕРУВАННЯ ФАЙЛАМИ ТАРУВАННЯ ТА ФОТО ===


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


@router.delete("/files/{file_id}")
def delete_tare_file(file_id: int, db: DbSession):
    db_file = db.query(VehicleFile).filter(VehicleFile.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="Файл не знайдено")
    db_file.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return {"message": "Файл переміщено в корзину"}
