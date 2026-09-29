from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class TarArchive(Base):
    __tablename__ = "tar_archives"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, index=True)
    original_vehicle_number = Column(String, nullable=True, index=True)
    file_path = Column(String, nullable=False)

    is_favorite = Column(Boolean, default=False)

    # Габарити та висоти (копіюються зі словника баку при першій прив'язці або вводяться вручну)
    nominal_volume = Column(Float, nullable=True)
    dim_l = Column(Float, nullable=True)
    dim_w = Column(Float, nullable=True)
    dim_h = Column(Float, nullable=True)
    h1 = Column(Float, nullable=True)
    h2 = Column(Float, nullable=True)
    no_neck_access = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    added_at = Column(DateTime(timezone=True), server_default=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Зв'язок: на яких баках стоїть цей еталонний ТАР
    tanks = relationship("FuelTank", back_populates="tar_archive")
