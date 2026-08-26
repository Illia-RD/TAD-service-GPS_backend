from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class VehicleFile(Base):
    __tablename__ = "vehicle_files"

    id = Column(Integer, primary_key=True, index=True)
    # nullable=True дозволяє файлу відв'язатись від авто і впасти в "Резерв" Архіву
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)
    file_name = Column(String, index=True)
    file_path = Column(String)
    file_type = Column(String, default="тарування")
    tank_index = Column(Integer, nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    # --- Дані лінійки ---
    h1 = Column(Float, nullable=True)
    h2 = Column(Float, nullable=True)
    no_neck_access = Column(Boolean, default=False)

    # === АРХІВНІ ДАНІ (ЗЛІПОК БАКА) ===
    is_etalon = Column(Boolean, default=False)
    tank_model_id = Column(Integer, ForeignKey("dict_tank_models.id"), nullable=True)
    actual_volume = Column(Float, nullable=True)
    tank_photo_path = Column(String, nullable=True)
    tank_notes = Column(Text, nullable=True)

    vehicle = relationship("Vehicle", back_populates="files")


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    internal_id = Column(String, unique=True, index=True, nullable=False)
    plate = Column(String, unique=True, index=True, nullable=False)
    make = Column(String, nullable=False)
    model = Column(String, nullable=False)
    vin = Column(String, nullable=True)
    year = Column(Integer, nullable=True)
    euro_standard = Column(String, nullable=True)
    group_name = Column(String, default="Без групи")

    status = Column(String, default="connected")
    other_equipment = Column(String, nullable=True)

    trackers_data = Column(JSON, default=list)
    tanks_data = Column(JSON, default=list)
    drps_data = Column(JSON, default=list)
    notes = Column(Text, nullable=True)

    # --- ПОЛЕ ДЛЯ КОРЗИНИ ---
    deleted_at = Column(DateTime, nullable=True, default=None)

    tickets = relationship(
        "Ticket", back_populates="vehicle", cascade="all, delete-orphan"
    )
    files = relationship(
        "VehicleFile",
        back_populates="vehicle",
        cascade="all, delete-orphan",
        primaryjoin="and_(Vehicle.id == VehicleFile.vehicle_id, VehicleFile.deleted_at == None)",
    )
