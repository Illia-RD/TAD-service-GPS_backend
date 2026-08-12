from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class VehicleFile(Base):
    __tablename__ = "vehicle_files"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id", ondelete="CASCADE"))
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, default="тарування")

    # --- НОВЕ ПОЛЕ ДЛЯ ПРИВ'ЯЗКИ ДО КОНКРЕТНОГО БАКУ ---
    tank_index = Column(Integer, nullable=True, default=None)

    # --- ПОЛЕ ДЛЯ КОРЗИНИ ---
    deleted_at = Column(DateTime, nullable=True, default=None)

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
