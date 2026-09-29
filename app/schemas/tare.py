from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TarArchiveBase(BaseModel):
    file_name: str
    original_vehicle_number: str | None = None
    is_favorite: bool = False

    # Габарити та висоти (переїхали сюди)
    nominal_volume: float | None = None
    dim_l: float | None = None
    dim_w: float | None = None
    dim_h: float | None = None
    h1: float | None = None
    h2: float | None = None
    no_neck_access: bool = False


class TarArchiveUpdate(BaseModel):
    file_name: str | None = None
    original_vehicle_number: str | None = None
    is_favorite: bool | None = None

    nominal_volume: float | None = None
    dim_l: float | None = None
    dim_w: float | None = None
    dim_h: float | None = None
    h1: float | None = None
    h2: float | None = None
    no_neck_access: bool | None = None


class TarArchiveResponse(TarArchiveBase):
    id: int
    file_path: str
    added_at: datetime
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
