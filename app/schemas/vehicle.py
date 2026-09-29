from pydantic import BaseModel, ConfigDict, Field

from .equipment import (
    LlsSensorCreate,
    LlsSensorResponse,
    TrackerResponse,
)


# --- Vehicle Files (Очищено від тарування) ---
class VehicleFileResponse(BaseModel):
    id: int
    file_name: str
    file_path: str
    file_type: str | None = "документ"
    model_config = ConfigDict(from_attributes=True)


# --- Fuel Tanks (Перенесено сюди з equipment) ---
class FuelTankBase(BaseModel):
    tank_model_id: int | None = None
    tar_archive_id: int | None = None  # Прив'язка до еталонного ТАР файлу
    tank_volume: float | None = None
    actual_volume: float | None = None
    notes: str | None = None
    photo_paths: list[str] = Field(default_factory=list)


class FuelTankCreate(FuelTankBase):
    pass


class FuelTankResponse(FuelTankBase):
    id: int
    vehicle_id: int
    model_config = ConfigDict(from_attributes=True)


# --- Vehicle ---
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
