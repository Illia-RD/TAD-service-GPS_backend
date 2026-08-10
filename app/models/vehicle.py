from sqlalchemy import JSON, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class VehicleFile(Base):
    __tablename__ = "vehicle_files"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id", ondelete="CASCADE"))
    file_name = Column(
        String, nullable=False
    )  # Оригінальна назва файлу (напр. tank1.csv)
    file_path = Column(String, nullable=False)  # Де він лежить на сервері
    file_type = Column(String, default="тарування")

    vehicle = relationship("Vehicle", back_populates="files")


class Vehicle(Base):
    __tablename__ = "vehicles"

    # Базова інформація про авто
    id = Column(Integer, primary_key=True, index=True)
    internal_id = Column(String, unique=True, index=True, nullable=False)
    plate = Column(String, unique=True, index=True, nullable=False)
    make = Column(String, nullable=False)
    model = Column(String, nullable=False)
    vin = Column(String, nullable=True)
    year = Column(Integer, nullable=True)
    euro_standard = Column(String, nullable=True)
    group_name = Column(String, default="Без групи")

    # --- НОВІ КОЛОНКИ ---
    status = Column(String, default="connected")
    other_equipment = Column(String, nullable=True)

    # Гнучкі поля для незалежного обліку обладнання
    trackers_data = Column(JSON, default=list)
    tanks_data = Column(JSON, default=list)
    drps_data = Column(JSON, default=list)
    notes = Column(Text, nullable=True)
    # Зв'язок із сервісними заявками (тікетами)
    tickets = relationship(
        "Ticket", back_populates="vehicle", cascade="all, delete-orphan"
    )
    files = relationship(
        "VehicleFile", back_populates="vehicle", cascade="all, delete-orphan"
    )
