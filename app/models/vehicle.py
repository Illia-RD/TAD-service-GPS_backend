from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base  # Імпортуємо Base з core


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    plate = Column(String(20), unique=True, index=True, nullable=False)
    vin = Column(String(17), unique=True, index=True, nullable=False)
    model = Column(String(100), nullable=False)
    year = Column(Integer, nullable=True)

    tank_volume = Column(Integer, nullable=True)
    tank_dimensions = Column(String(50), nullable=True)
    tracker_model = Column(String(50), nullable=True)
    tracker_imei = Column(String(50), unique=True, nullable=True)

    traccar_device_id = Column(Integer, unique=True, nullable=True)
    is_monitoring_arrival = Column(Boolean, default=False)

    # Зв'язок з тікетами
    # Увага: вказуємо назву класу рядком "Ticket", щоб уникнути проблем з імпортом
    tickets = relationship(
        "Ticket", back_populates="vehicle", cascade="all, delete-orphan"
    )
