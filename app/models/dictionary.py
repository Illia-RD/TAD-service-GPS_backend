from sqlalchemy import JSON, Boolean, Column, Float, Integer, String

from app.core.database import Base


class VehicleMake(Base):
    __tablename__ = "dict_vehicle_makes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)


class VehicleModel(Base):
    __tablename__ = "dict_vehicle_models"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)


class LlsModel(Base):
    __tablename__ = "dict_lls_models"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)


class TaskTemplate(Base):
    __tablename__ = "dict_task_templates"
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


class SimNetworkStatus(Base):
    __tablename__ = "dict_sim_network_statuses"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)


class VehicleGroup(Base):
    __tablename__ = "dict_vehicle_groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)


class TankModel(Base):
    __tablename__ = "dict_tank_models"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    shape_type = Column(String, default="rectangular")
    nominal_volume = Column(Float, nullable=True)
    dim_l = Column(Float, nullable=True)
    dim_w = Column(Float, nullable=True)
    dim_h = Column(Float, nullable=True)
    step_l = Column(Float, nullable=True)
    step_w = Column(Float, nullable=True)
    step_h = Column(Float, nullable=True)


class CustomFieldTemplate(Base):
    """Шаблони для конструктора форми (динамічні поля)"""

    __tablename__ = "dict_custom_field_templates"
    id = Column(Integer, primary_key=True, index=True)
    department = Column(String, index=True)  # Напр., "Електрика", "Механіка", "РВА"
    field_name = Column(String, nullable=False)  # Напр., "Проблисковий маячок"
    field_type = Column(String, default="text")  # "text", "number", "boolean", "select"
    options = Column(JSON, nullable=True)  # Якщо select - тут масив ["Hella", "Bosch"]
    is_required = Column(Boolean, default=False)
