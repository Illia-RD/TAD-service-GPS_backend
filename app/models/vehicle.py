from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    plate = Column(String, unique=True, index=True)
    vin = Column(String)
    make = Column(String)
    model = Column(String)
    internal_id = Column(String)
    year = Column(Integer)
    euro_standard = Column(String)  # "Euro 4", "Euro 5", "Euro 6"
    group_name = Column(String, default="Без групи")  # Для групування
    # Паливо
    tank_volume = Column(Float)
    tank_dimensions = Column(String)

    # Обладнання
    tracker_model = Column(String)
    tracker_sn = Column(String)
    tracker_imei = Column(String)
    sim_operator = Column(String)
    sim_number = Column(String)
    drp_type = Column(String)
    drp_height = Column(Float)
    other_equipment = Column(String)

    # Ось той зв'язок, який шукає Ticket
    tickets = relationship(
        "Ticket", back_populates="vehicle", cascade="all, delete-orphan"
    )
