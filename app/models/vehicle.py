from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, JSON, Text, DateTime
from sqlalchemy.orm import relationship
from .base import Base


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

    # JSON поле для кастомних атрибутів (Конструктор)
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
