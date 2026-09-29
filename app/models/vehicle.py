from sqlalchemy import (
    JSON,
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
    notes = Column(Text, nullable=True)
    custom_fields = Column(JSON, default=dict, nullable=False)
    deleted_at = Column(DateTime, nullable=True, default=None)

    trackers = relationship(
        "Tracker",
        back_populates="vehicle",
        primaryjoin="and_(Vehicle.id == Tracker.vehicle_id, Tracker.deleted_at == None)",
    )
    tanks = relationship(
        "FuelTank", back_populates="vehicle", cascade="all, delete-orphan"
    )
    lls_sensors = relationship(
        "LlsSensor", back_populates="vehicle", cascade="all, delete-orphan"
    )
    files = relationship(
        "VehicleFile",
        back_populates="vehicle",
        primaryjoin="and_(Vehicle.id == VehicleFile.vehicle_id, VehicleFile.deleted_at == None)",
    )
    tickets = relationship(
        "Ticket", back_populates="vehicle", cascade="all, delete-orphan"
    )


class FuelTank(Base):
    __tablename__ = "fuel_tanks"
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(
        Integer, ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False
    )

    # Словник габаритів
    tank_model_id = Column(Integer, ForeignKey("dict_tank_models.id"), nullable=True)

    # Зв'язок з ТАР-архівом (Один ТАР може бути на багатьох баках)
    tar_archive_id = Column(
        Integer, ForeignKey("tar_archives.id", ondelete="SET NULL"), nullable=True
    )

    tank_volume = Column(Float, nullable=True)
    actual_volume = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    photo_paths = Column(JSON, default=list)

    vehicle = relationship("Vehicle", back_populates="tanks")
    tar_archive = relationship("TarArchive", back_populates="tanks")
    lls_sensors = relationship("LlsSensor", back_populates="tank")


class VehicleFile(Base):
    __tablename__ = "vehicle_files"
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(
        Integer, ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=True
    )
    file_name = Column(String, index=True)
    file_path = Column(String)
    file_type = Column(String, default="документ")  # Більше ніяких h1, h2 тут немає
    deleted_at = Column(DateTime, nullable=True)

    vehicle = relationship("Vehicle", back_populates="files")
