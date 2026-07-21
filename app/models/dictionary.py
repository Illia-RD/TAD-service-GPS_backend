from sqlalchemy import Column, Integer, String

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
