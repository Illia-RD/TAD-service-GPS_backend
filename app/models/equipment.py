from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class EquipmentHistory(Base):
    __tablename__ = "equipment_history"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, server_default=func.now())
    action = Column(String, nullable=False)
    note = Column(Text, nullable=True)

    tracker_id = Column(
        Integer, ForeignKey("trackers.id", ondelete="CASCADE"), nullable=True
    )
    lls_sensor_id = Column(
        Integer, ForeignKey("lls_sensors.id", ondelete="CASCADE"), nullable=True
    )
    sim_card_id = Column(
        Integer, ForeignKey("sim_cards.id", ondelete="CASCADE"), nullable=True
    )
    vehicle_id = Column(
        Integer, ForeignKey("vehicles.id", ondelete="SET NULL"), nullable=True
    )

    tracker = relationship("Tracker", back_populates="history")
    lls_sensor = relationship("LlsSensor", back_populates="history")
    sim_card = relationship("SimCard", back_populates="history")
    vehicle = relationship("Vehicle")


class Tracker(Base):
    __tablename__ = "trackers"
    id = Column(Integer, primary_key=True, index=True)
    imei = Column(String, unique=True, index=True, nullable=False)
    model = Column(String, nullable=True)
    serial_number = Column(String, nullable=True)
    sent_id = Column(String, nullable=True)
    status = Column(String, default="in_stock")
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    vehicle = relationship("Vehicle", back_populates="trackers")
    sim_cards = relationship("SimCard", back_populates="tracker")
    history = relationship(
        "EquipmentHistory", back_populates="tracker", cascade="all, delete-orphan"
    )


class SimCard(Base):
    __tablename__ = "sim_cards"
    id = Column(Integer, primary_key=True, index=True)
    short_id = Column(String, unique=True, index=True, nullable=False)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    iccid = Column(String, unique=True, nullable=True)
    operator = Column(String, nullable=True)
    condition = Column(String, default="new")
    network_status = Column(String, default="Призупинена")
    tracker_id = Column(Integer, ForeignKey("trackers.id"), nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    tracker = relationship("Tracker", back_populates="sim_cards")
    history = relationship(
        "EquipmentHistory", back_populates="sim_card", cascade="all, delete-orphan"
    )


class LlsSensor(Base):
    __tablename__ = "lls_sensors"
    id = Column(Integer, primary_key=True, index=True)

    vehicle_id = Column(
        Integer, ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=True
    )
    tank_id = Column(
        Integer, ForeignKey("fuel_tanks.id", ondelete="SET NULL"), nullable=True
    )

    lls_model = Column(String, nullable=True)
    serial_number = Column(String, nullable=True)
    lls_height = Column(Float, nullable=True)
    connection_type = Column(String, default="RS485")
    status = Column(String, default="in_stock")

    vehicle = relationship("Vehicle", back_populates="lls_sensors")
    tank = relationship("FuelTank", back_populates="lls_sensors")
    history = relationship(
        "EquipmentHistory", back_populates="lls_sensor", cascade="all, delete-orphan"
    )
