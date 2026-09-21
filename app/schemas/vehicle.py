from pydantic import BaseModel, ConfigDict, Field

from .equipment import (
    FuelTankCreate,
    FuelTankResponse,
    LlsSensorCreate,
    LlsSensorResponse,
    TrackerResponse,
)


class VehicleFileResponse(BaseModel):
    id: int
    file_name: str
    file_path: str
    file_type: str | None = "тарування"
    tank_index: int | None = None
    h1: float | None = None
    h2: float | None = None
    no_neck_access: bool | None = False
    model_config = ConfigDict(from_attributes=True)


class VehicleBase(BaseModel):
    internal_id: str
    plate: str
    make: str
    model: str
    vin: str | None = None
    year: int | None = None
    euro_standard: str | None = None
    group_name: str | None = "Без групи"
    status: str | None = "connected"
    other_equipment: str | None = None
    notes: str | None = None
    custom_fields: dict = Field(default_factory=dict)  # Для конструктора


class VehicleCreate(VehicleBase):
    # При створенні можемо одразу передавати масиви баків та датчиків
    tanks: list[FuelTankCreate] = Field(default_factory=list)
    lls_sensors: list[LlsSensorCreate] = Field(default_factory=list)


class VehicleUpdate(VehicleBase):
    tanks: list[FuelTankCreate] = Field(default_factory=list)
    lls_sensors: list[LlsSensorCreate] = Field(default_factory=list)


class VehicleResponse(VehicleBase):
    id: int
    tanks: list[FuelTankResponse] = Field(default_factory=list)
    lls_sensors: list[LlsSensorResponse] = Field(default_factory=list)
    trackers: list[TrackerResponse] = Field(default_factory=list)
    files: list[VehicleFileResponse] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)
