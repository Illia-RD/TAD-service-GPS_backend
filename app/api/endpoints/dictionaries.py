from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.dictionary import (
    DrpType,
    EuroStandard,
    SimOperator,
    TankModel,
    TaskTemplate,
    TrackerModel,
    VehicleGroup,
    VehicleMake,
    VehicleModel,
)
from app.schemas.dictionary import (
    DictItemCreate,
    DictItemResponse,
    TankModelCreate,
    TankModelResponse,
)

router = APIRouter()

# Використовуємо Annotated, щоб Ruff не матюкався на B008
DbSession = Annotated[Session, Depends(get_db)]


def get_or_create(db: Session, model_class, name: str):
    item = db.query(model_class).filter(model_class.name == name).first()
    if item:
        return item
    new_item = model_class(name=name)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@router.get("/makes", response_model=list[DictItemResponse])
def get_makes(db: DbSession):
    return db.query(VehicleMake).all()


@router.post("/makes", response_model=DictItemResponse)
def create_make(item: DictItemCreate, db: DbSession):
    return get_or_create(db, VehicleMake, item.name)


@router.get("/drp-types", response_model=list[DictItemResponse])
def get_drp_types(db: DbSession):
    return db.query(DrpType).all()


@router.post("/drp-types", response_model=DictItemResponse)
def create_drp_type(item: DictItemCreate, db: DbSession):
    return get_or_create(db, DrpType, item.name)


@router.get("/tasks", response_model=list[DictItemResponse])
def get_tasks(db: DbSession):
    return db.query(TaskTemplate).all()


@router.post("/tasks", response_model=DictItemResponse)
def create_task(item: DictItemCreate, db: DbSession):
    return get_or_create(db, TaskTemplate, item.name)


@router.get("/models", response_model=list[DictItemResponse])
def get_models(db: DbSession):
    return db.query(VehicleModel).all()


@router.post("/models", response_model=DictItemResponse)
def create_model(item: DictItemCreate, db: DbSession):
    return get_or_create(db, VehicleModel, item.name)


@router.get("/euro-standards", response_model=list[DictItemResponse])
def get_euro(db: DbSession):
    return db.query(EuroStandard).all()


@router.post("/euro-standards", response_model=DictItemResponse)
def create_euro(item: DictItemCreate, db: DbSession):
    return get_or_create(db, EuroStandard, item.name)


@router.get("/tracker-models", response_model=list[DictItemResponse])
def get_trackers(db: DbSession):
    return db.query(TrackerModel).all()


@router.post("/tracker-models", response_model=DictItemResponse)
def create_tracker(item: DictItemCreate, db: DbSession):
    return get_or_create(db, TrackerModel, item.name)


@router.get("/sim-operators", response_model=list[DictItemResponse])
def get_sims(db: DbSession):
    return db.query(SimOperator).all()


@router.post("/sim-operators", response_model=DictItemResponse)
def create_sim(item: DictItemCreate, db: DbSession):
    return get_or_create(db, SimOperator, item.name)


@router.get("/groups", response_model=list[DictItemResponse])
def get_groups(db: DbSession):
    return db.query(VehicleGroup).all()


@router.post("/groups", response_model=DictItemResponse)
def create_group(item: DictItemCreate, db: DbSession):
    return get_or_create(db, VehicleGroup, item.name)


# --- ДОВІДНИК БАКІВ (КАТАЛОГ) ---
@router.get("/tank-models", response_model=list[TankModelResponse])
def get_tank_models(db: DbSession):
    return db.query(TankModel).all()


@router.post("/tank-models", response_model=TankModelResponse)
def create_tank_model(item: TankModelCreate, db: DbSession):
    db_item = TankModel(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
