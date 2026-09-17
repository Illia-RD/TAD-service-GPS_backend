from datetime import datetime, timezone

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


# === НОВЕ: ТАБЛИЦЯ ТРЕКЕРІВ ===
class Tracker(Base):
    __tablename__ = "trackers"

    id = Column(Integer, primary_key=True, index=True)
    imei = Column(String, unique=True, index=True, nullable=False)
    model = Column(String, nullable=True)
    serial_number = Column(String, nullable=True)
    sent_id = Column(String, nullable=True)  # ID для польської системи SENT

    # Статуси: new, used, broken, repair, diagnostics
    status = Column(String, default="new")

    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    vehicle = relationship("Vehicle", back_populates="trackers")
    sim_cards = relationship("SimCard", back_populates="tracker")


# === НОВЕ: ТАБЛИЦЯ СІМ-КАРТ ===
class SimCard(Base):
    __tablename__ = "sim_cards"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    iccid = Column(String, unique=True, nullable=True)
    operator = Column(String, nullable=True)

    # Статуси: new, active, problematic, deactivated
    status = Column(String, default="new")

    tracker_id = Column(Integer, ForeignKey("trackers.id"), nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    tracker = relationship("Tracker", back_populates="sim_cards")


# === НОВЕ: ІСТОРІЯ РУХУ ОБЛАДНАННЯ ===
class EquipmentLog(Base):
    __tablename__ = "equipment_logs"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String, nullable=False)  # 'tracker' або 'sim'
    entity_id = Column(Integer, nullable=False)
    action = Column(String, nullable=False)  # 'installed', 'removed', 'status_changed'
    description = Column(Text, nullable=True)

    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


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

    # Трекери тепер не JSON, а повноцінний зв'язок!
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

    # Зв'язок з трекерами
    trackers = relationship(
        "Tracker",
        back_populates="vehicle",
        primaryjoin="and_(Vehicle.id == Tracker.vehicle_id, Tracker.deleted_at == None)",
    )
