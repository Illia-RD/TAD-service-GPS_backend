from pydantic import BaseModel, ConfigDict, Field


# --- SIM Cards ---
class SimCardBase(BaseModel):
    short_id: str | None = None  # Необов'язкове при створенні, згенеруємо самі
    phone_number: str
    iccid: str | None = None
    operator: str | None = None
    condition: str = "new"
    network_status: str | None = "Призупинена"


class SimCardCreate(SimCardBase):
    pass


class SimCardResponse(SimCardBase):
    id: int
    tracker_id: int | None = None
    model_config = ConfigDict(from_attributes=True)


# --- Trackers ---
class TrackerBase(BaseModel):
    imei: str
    model: str | None = None
    serial_number: str | None = None
    sent_id: str | None = None
    status: str = "new"


class TrackerCreate(TrackerBase):
    pass


class TrackerResponse(TrackerBase):
    id: int
    vehicle_id: int | None = None
    sim_cards: list[SimCardResponse] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)


# --- Fuel Tanks ---
class FuelTankBase(BaseModel):
    tank_model_id: int | None = None
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


# --- LLS Sensors (ДВРП) ---
class LlsSensorBase(BaseModel):
    tank_id: int | None = None
    lls_model: str | None = None  # Замість drp_type
    serial_number: str | None = None
    lls_height: float | None = None  # Замість drp_height
    connection_type: str | None = "RS485"


class LlsSensorCreate(LlsSensorBase):
    pass


class LlsSensorResponse(LlsSensorBase):
    id: int
    vehicle_id: int | None = None
    model_config = ConfigDict(from_attributes=True)
