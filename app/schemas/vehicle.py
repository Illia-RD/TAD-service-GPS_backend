from typing import List, Optional

from pydantic import BaseModel, Field

# --- ДОПОМІЖНІ МОДЕЛІ ДЛЯ ОБЛАДНАННЯ ---


class TankItem(BaseModel):
    id: str  # Унікальний ID баку (наприклад, згенерований uuid на фронті)
    tank_volume: Optional[float] = None
    tank_dimensions: Optional[str] = None
    # Масив drps звідси повністю прибрали


class DrpItem(BaseModel):
    id: str  # Унікальний ID датчика
    drp_type: Optional[str] = None
    drp_height: Optional[float] = None
    tank_id: str  # Зв'язок: вказує, в який саме бак врізано цей ДВРП


class TrackerItem(BaseModel):
    id: str  # Унікальний ID трекера
    tracker_model: Optional[str] = None
    tracker_sn: Optional[str] = None
    tracker_imei: Optional[str] = None
    sim_operator: Optional[str] = None
    sim_number: Optional[str] = None


# --- ОСНОВНІ СХЕМИ АВТОМОБІЛЯ ---


class VehicleBase(BaseModel):
    internal_id: str
    plate: str
    make: str
    model: str
    vin: Optional[str] = None
    year: Optional[int] = None
    euro_standard: Optional[str] = None
    group_name: Optional[str] = "Без групи"

    # 4 незалежних масиви з обладнанням
    trackers_data: List[TrackerItem] = Field(default_factory=list)
    tanks_data: List[TankItem] = Field(default_factory=list)
    drps_data: List[DrpItem] = Field(default_factory=list)
    additional_equipment: List[str] = Field(default_factory=list)


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(VehicleBase):
    pass


class VehicleResponse(VehicleBase):
    id: int

    class Config:
        from_attributes = True
