from sqlalchemy import Column, Float, Integer, String

from app.core.database import Base


class VehicleMake(Base):
    __tablename__ = "dict_vehicle_makes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)


class DrpType(Base):
    __tablename__ = "dict_drp_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)


class TaskTemplate(Base):
    __tablename__ = "dict_task_templates"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)


# --- НОВІ ДОВІДНИКИ ---
class VehicleModel(Base):
    __tablename__ = "dict_vehicle_models"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)


class EuroStandard(Base):
    __tablename__ = "dict_euro_standards"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)


class TrackerModel(Base):
    __tablename__ = "dict_tracker_models"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)


class SimOperator(Base):
    __tablename__ = "dict_sim_operators"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)


class VehicleGroup(Base):
    __tablename__ = "dict_vehicle_groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)


# === НОВИЙ ДОВІДНИК: КАТАЛОГ ТИПІВ БАКІВ ===
class TankModel(Base):
    __tablename__ = "dict_tank_models"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    shape_type = Column(String, default="rectangular")
    nominal_volume = Column(Float, nullable=True)

    # Основні габарити
    dim_l = Column(Float, nullable=True)
    dim_w = Column(Float, nullable=True)
    dim_h = Column(Float, nullable=True)

    # Габарити вирізу/сходинки
    step_l = Column(Float, nullable=True)
    step_w = Column(Float, nullable=True)
    step_h = Column(Float, nullable=True)
