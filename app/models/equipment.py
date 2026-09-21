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

from .base import Base


class Tracker(Base):
    __tablename__ = "trackers"
    id = Column(Integer, primary_key=True, index=True)
    imei = Column(String, unique=True, index=True, nullable=False)
    model = Column(String, nullable=True)
    serial_number = Column(String, nullable=True)
    sent_id = Column(String, nullable=True)
    status = Column(String, default="new")
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    vehicle = relationship("Vehicle", back_populates="trackers")
    sim_cards = relationship("SimCard", back_populates="tracker")


class SimCard(Base):
    __tablename__ = "sim_cards"
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    iccid = Column(String, unique=True, nullable=True)
    operator = Column(String, nullable=True)
    status = Column(String, default="new")
    tracker_id = Column(Integer, ForeignKey("trackers.id"), nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    tracker = relationship("Tracker", back_populates="sim_cards")


class FuelTank(Base):
    __tablename__ = "fuel_tanks"
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(
        Integer, ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False
    )
    tank_model_id = Column(Integer, ForeignKey("dict_tank_models.id"), nullable=True)

    tank_volume = Column(Float, nullable=True)
    actual_volume = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    photo_paths = Column(JSON, default=list)

    vehicle = relationship("Vehicle", back_populates="tanks")
    lls_sensors = relationship("LlsSensor", back_populates="tank")


class LlsSensor(Base):
    __tablename__ = "lls_sensors"
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(
        Integer, ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False
    )
    tank_id = Column(
        Integer, ForeignKey("fuel_tanks.id", ondelete="SET NULL"), nullable=True
    )

    lls_model = Column(String, nullable=True)  # замість drp_type
    serial_number = Column(String, nullable=True)
    lls_height = Column(Float, nullable=True)  # замість drp_height
    connection_type = Column(String, default="RS485")

    vehicle = relationship("Vehicle", back_populates="lls_sensors")
    tank = relationship("FuelTank", back_populates="lls_sensors")


class VehicleFile(Base):
    __tablename__ = "vehicle_files"
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)
    file_name = Column(String, index=True)
    file_path = Column(String)
    file_type = Column(String, default="тарування")
    tank_index = Column(Integer, nullable=True)
    h1 = Column(Float, nullable=True)
    h2 = Column(Float, nullable=True)
    no_neck_access = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)

    vehicle = relationship("Vehicle", back_populates="files")
