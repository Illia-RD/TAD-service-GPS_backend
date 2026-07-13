from pydantic import BaseModel
from typing import Optional

class VehicleSchema(BaseModel):
    id: int
    plate: str
    vin: str
    model: str
    tracker_model: Optional[str] = None

    class Config:
        from_attributes = True