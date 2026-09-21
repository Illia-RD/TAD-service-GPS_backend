from fastapi import APIRouter, HTTPException

from app.api.dependencies import DbSession
from app.models.equipment import SimCard, Tracker
from app.schemas.equipment import (
    SimCardCreate,
    SimCardResponse,
    TrackerCreate,
    TrackerResponse,
)

router = APIRouter()

# --- ТРЕКЕРИ ---


@router.get("/trackers/archive", response_model=list[TrackerResponse])
def get_archive_trackers(db: DbSession):
    # Віддаємо тільки ті трекери, які лежать на складі (не прив'язані до авто)
    return db.query(Tracker).filter(Tracker.vehicle_id.is_(None)).all()


@router.post("/trackers", response_model=TrackerResponse)
def create_tracker(tracker: TrackerCreate, db: DbSession):
    db_tracker = Tracker(**tracker.model_dump())
    db.add(db_tracker)
    db.commit()
    db.refresh(db_tracker)
    return db_tracker


@router.post("/trackers/{tracker_id}/assign/{vehicle_id}")
def assign_tracker(tracker_id: int, vehicle_id: int, db: DbSession):
    tracker = db.query(Tracker).filter(Tracker.id == tracker_id).first()
    if not tracker:
        raise HTTPException(status_code=404, detail="Трекер не знайдено")
    tracker.vehicle_id = vehicle_id
    tracker.status = "installed"
    db.commit()
    return {"message": "Трекер прив'язано до авто"}


@router.post("/trackers/{tracker_id}/unassign")
def unassign_tracker(tracker_id: int, db: DbSession):
    tracker = db.query(Tracker).filter(Tracker.id == tracker_id).first()
    if not tracker:
        raise HTTPException(status_code=404, detail="Трекер не знайдено")
    tracker.vehicle_id = None
    tracker.status = "used"  # Зняли — отже, вже б/в
    db.commit()
    return {"message": "Трекер знято і повернено на склад"}


# --- СІМ-КАРТИ ---


@router.get("/sim-cards/archive", response_model=list[SimCardResponse])
def get_archive_sims(db: DbSession):
    # Віддаємо тільки вільні сімки
    return db.query(SimCard).filter(SimCard.tracker_id.is_(None)).all()


@router.post("/sim-cards", response_model=SimCardResponse)
def create_sim(sim: SimCardCreate, db: DbSession):
    db_sim = SimCard(**sim.model_dump())
    db.add(db_sim)
    db.commit()
    db.refresh(db_sim)
    return db_sim


@router.post("/sim-cards/{sim_id}/assign/{tracker_id}")
def assign_sim(sim_id: int, tracker_id: int, db: DbSession):
    sim = db.query(SimCard).filter(SimCard.id == sim_id).first()
    if not sim:
        raise HTTPException(status_code=404, detail="СІМ-карту не знайдено")
    sim.tracker_id = tracker_id
    sim.status = "active"
    db.commit()
    return {"message": "СІМ-карту вставлено в трекер"}


@router.post("/sim-cards/{sim_id}/unassign")
def unassign_sim(sim_id: int, db: DbSession):
    sim = db.query(SimCard).filter(SimCard.id == sim_id).first()
    if not sim:
        raise HTTPException(status_code=404, detail="СІМ-карту не знайдено")
    sim.tracker_id = None
    sim.status = "used"
    db.commit()
    return {"message": "СІМ-карту витягнуто"}
