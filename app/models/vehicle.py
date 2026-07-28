from sqlalchemy import JSON, Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


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
    # additional_equipment ВИДАЛЕНО, бо тепер є other_equipment

    # Зв'язок із сервісними заявками (тікетами)
    tickets = relationship(
        "Ticket", back_populates="vehicle", cascade="all, delete-orphan"
    )
