from fastapi import APIRouter, HTTPException

from app.api.dependencies import DbSession
from app.models.equipment import EquipmentHistory, LlsSensor, SimCard, Tracker
from app.schemas.equipment import (
    LlsSensorCreate,
    LlsSensorResponse,
    SimCardCreate,
    SimCardResponse,
    TrackerCreate,
    TrackerResponse,
)

router = APIRouter()


def log_history(
    db: DbSession,
    action: str,
    note: str,
    tracker_id=None,
    lls_sensor_id=None,
    sim_card_id=None,
    vehicle_id=None,
):
    """Допоміжна функція для запису історії рухів"""
    history = EquipmentHistory(
        action=action,
        note=note,
        tracker_id=tracker_id,
        lls_sensor_id=lls_sensor_id,
        sim_card_id=sim_card_id,
        vehicle_id=vehicle_id,
    )
    db.add(history)


# --- ТРЕКЕРИ ---


@router.get("/trackers/archive", response_model=list[TrackerResponse])
def get_archive_trackers(db: DbSession):
    return db.query(Tracker).filter(Tracker.vehicle_id.is_(None)).all()


@router.post("/trackers", response_model=TrackerResponse)
def create_tracker(tracker: TrackerCreate, db: DbSession):
    db_tracker = Tracker(**tracker.model_dump())
    db.add(db_tracker)
    db.commit()
    db.refresh(db_tracker)
    log_history(db, "created", "Прийнято на склад", tracker_id=db_tracker.id)
    db.commit()
    return db_tracker


@router.post("/trackers/{tracker_id}/assign/{vehicle_id}")
def assign_tracker(tracker_id: int, vehicle_id: int, db: DbSession):
    tracker = db.query(Tracker).filter(Tracker.id == tracker_id).first()
    if not tracker:
        raise HTTPException(status_code=404, detail="Трекер не знайдено")
    tracker.vehicle_id = vehicle_id
    tracker.status = "installed"
    log_history(
        db,
        "installed",
        "Встановлено на авто",
        tracker_id=tracker_id,
        vehicle_id=vehicle_id,
    )
    db.commit()
    return {"message": "Трекер прив'язано до авто"}


@router.post("/trackers/{tracker_id}/unassign")
def unassign_tracker(tracker_id: int, db: DbSession):
    tracker = db.query(Tracker).filter(Tracker.id == tracker_id).first()
    if not tracker:
        raise HTTPException(status_code=404, detail="Трекер не знайдено")
    old_vehicle_id = tracker.vehicle_id
    tracker.vehicle_id = None
    tracker.status = "used"
    log_history(
        db,
        "uninstalled",
        "Знято з авто на склад",
        tracker_id=tracker_id,
        vehicle_id=old_vehicle_id,
    )
    db.commit()
    return {"message": "Трекер знято і повернено на склад"}


# --- ДВРП (LLS) ---


@router.get("/lls/archive", response_model=list[LlsSensorResponse])
def get_archive_lls(db: DbSession):
    return db.query(LlsSensor).filter(LlsSensor.vehicle_id.is_(None)).all()


@router.post("/lls", response_model=LlsSensorResponse)
def create_lls(sensor: LlsSensorCreate, db: DbSession):
    db_sensor = LlsSensor(**sensor.model_dump())
    db.add(db_sensor)
    db.commit()
    db.refresh(db_sensor)
    log_history(db, "created", "Прийнято на склад", lls_sensor_id=db_sensor.id)
    db.commit()
    return db_sensor


@router.post("/lls/{sensor_id}/assign/{vehicle_id}")
def assign_lls(sensor_id: int, vehicle_id: int, db: DbSession):
    sensor = db.query(LlsSensor).filter(LlsSensor.id == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="ДВРП не знайдено")
    sensor.vehicle_id = vehicle_id
    sensor.status = "installed"
    log_history(
        db,
        "installed",
        "Встановлено на авто",
        lls_sensor_id=sensor_id,
        vehicle_id=vehicle_id,
    )
    db.commit()
    return {"message": "ДВРП прив'язано до авто"}


@router.post("/lls/{sensor_id}/unassign")
def unassign_lls(sensor_id: int, db: DbSession):
    sensor = db.query(LlsSensor).filter(LlsSensor.id == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="ДВРП не знайдено")
    old_vehicle_id = sensor.vehicle_id
    sensor.vehicle_id = None
    sensor.tank_id = None  # Знімаємо з бака теж
    sensor.status = "used"
    log_history(
        db,
        "uninstalled",
        "Знято з авто на склад",
        lls_sensor_id=sensor_id,
        vehicle_id=old_vehicle_id,
    )
    db.commit()
    return {"message": "ДВРП знято і повернено на склад"}


# --- СІМ-КАРТИ ---


@router.get("/sim-cards/archive", response_model=list[SimCardResponse])
def get_archive_sims(db: DbSession):
    return db.query(SimCard).filter(SimCard.tracker_id.is_(None)).all()


@router.post("/sim-cards", response_model=SimCardResponse)
def create_sim(sim: SimCardCreate, db: DbSession):
    sim_data = sim.model_dump()

    # Автогенерація short_id (00001, 00002...), якщо не передано з фронту
    if not sim_data.get("short_id"):
        last_sim = db.query(SimCard).order_by(SimCard.id.desc()).first()
        if last_sim and last_sim.short_id and last_sim.short_id.isdigit():
            next_id = int(last_sim.short_id) + 1
        else:
            next_id = db.query(SimCard).count() + 1
        sim_data["short_id"] = str(next_id).zfill(5)

    db_sim = SimCard(**sim_data)
    db.add(db_sim)
    db.commit()
    db.refresh(db_sim)
    log_history(
        db,
        "created",
        f"СІМ-картку {db_sim.short_id} додано на склад",
        sim_card_id=db_sim.id,
    )
    return db_sim


@router.post("/sim-cards/{sim_id}/assign/{tracker_id}")
def assign_sim(sim_id: int, tracker_id: int, db: DbSession):
    sim = db.query(SimCard).filter(SimCard.id == sim_id).first()
    if not sim:
        raise HTTPException(status_code=404, detail="СІМ-карту не знайдено")
    sim.tracker_id = tracker_id

    # Автоматично робимо її Б/В при першій вставці
    if sim.condition == "new":
        sim.condition = "used"

    log_history(
        db,
        "installed",
        f"Вставлено в трекер ID {tracker_id}",
        sim_card_id=sim_id,
        tracker_id=tracker_id,
    )
    db.commit()
    return {"message": "СІМ-карту вставлено в трекер"}


@router.post("/sim-cards/{sim_id}/unassign")
def unassign_sim(sim_id: int, db: DbSession):
    sim = db.query(SimCard).filter(SimCard.id == sim_id).first()
    if not sim:
        raise HTTPException(status_code=404, detail="СІМ-карту не знайдено")
    old_tracker = sim.tracker_id
    sim.tracker_id = None
    # condition залишається "used" - бо вона вже була у використанні!
    log_history(
        db, "uninstalled", f"Витягнуто з трекера ID {old_tracker}", sim_card_id=sim_id
    )
    db.commit()
    return {"message": "СІМ-карту витягнуто"}
