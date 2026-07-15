from typing import Optional

from pydantic import BaseModel


class VehicleBase(BaseModel):
    plate: str
    vin: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    internal_id: Optional[str] = None

    # Ті самі нові поля, які не пропускав бекенд
    year: Optional[int] = None
    euro_standard: Optional[str] = None
    group_name: Optional[str] = "Без групи"

    tank_volume: Optional[float] = 0.0
    tank_dimensions: Optional[str] = None
    tracker_model: Optional[str] = None
    tracker_sn: Optional[str] = None
    tracker_imei: Optional[str] = None
    sim_operator: Optional[str] = None
    sim_number: Optional[str] = None
    drp_type: Optional[str] = None
    drp_height: Optional[float] = 0.0
    other_equipment: Optional[str] = None


class VehicleCreate(VehicleBase):
    pass


class VehicleSchema(VehicleBase):
    id: int

    class Config:
        from_attributes = True
