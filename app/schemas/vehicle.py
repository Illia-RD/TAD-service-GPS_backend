from pydantic import BaseModel


class VehicleBase(BaseModel):
    plate: str
    vin: str
    make: str
    model: str
    internal_id: str
    tank_volume: float
    tank_dimensions: str
    tracker_model: str
    tracker_sn: str
    tracker_imei: str
    sim_operator: str
    sim_number: str
    drp_type: str
    drp_height: float
    other_equipment: str


class VehicleCreate(VehicleBase):
    pass


class VehicleSchema(VehicleBase):
    id: int

    class Config:
        from_attributes = True
