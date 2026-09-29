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


# --- LLS Sensors (ДВРП) ---
class LlsSensorBase(BaseModel):
    tank_id: int | None = None
    lls_model: str | None = None
    serial_number: str | None = None
    lls_height: float | None = None
    connection_type: str | None = "RS485"
    status: str | None = "in_stock"  # Фікс статусу для складу


class LlsSensorCreate(LlsSensorBase):
    pass


class LlsSensorResponse(LlsSensorBase):
    id: int
    vehicle_id: int | None = None
    model_config = ConfigDict(from_attributes=True)
