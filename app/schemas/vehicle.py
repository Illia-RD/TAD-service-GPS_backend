from pydantic import BaseModel, Field

# --- ДОПОМІЖНІ МОДЕЛІ ДЛЯ ОБЛАДНАННЯ ---


class TankItem(BaseModel):
    id: str
    tank_volume: float | None = None
    tank_dimensions: str | None = None


class DrpItem(BaseModel):
    id: str
    drp_type: str | None = None
    drp_height: float | None = None
    tank_id: str
    serial_number: str | None = None  # <--- Твоє поле (СЕРІЙНИК ДВРП)
    connection_type: str | None = None  # <--- Твоє поле (ТИП ПІДКЛЮЧЕННЯ)


class TrackerItem(BaseModel):
    id: str
    tracker_model: str | None = None
    tracker_imei: str | None = None  # <--- Твоє поле (IMEI)
    tracker_serial: str | None = None  # <--- Твоє поле (СЕРІЙНИК ТРЕКЕРА)
    sim_operator: str | None = None
    sim_number: str | None = None
    installation_location: str | None = None  # <--- Твоє поле (МІСЦЕ ВСТАНОВЛЕННЯ)


# --- НОВА СХЕМА ДЛЯ ФАЙЛІВ ТАРУВАННЯ ---
class VehicleFileResponse(BaseModel):
    id: int
    file_name: str
    file_path: str
    file_type: str | None = "тарування"

    class Config:
        from_attributes = True


# --- ОСНОВНІ СХЕМИ АВТОМОБІЛЯ ---


class VehicleBase(BaseModel):
    internal_id: str
    plate: str
    make: str
    model: str
    vin: str | None = None
    year: int | None = None
    euro_standard: str | None = None
    group_name: str | None = "Без групи"
    status: str | None = "connected"  # <--- Твоє поле (СТАТУС)

    trackers_data: list[TrackerItem] = Field(default_factory=list)
    tanks_data: list[TankItem] = Field(default_factory=list)
    drps_data: list[DrpItem] = Field(default_factory=list)
    other_equipment: str | None = None  # <--- Твоє поле (ІНШЕ ОБЛАДНАННЯ)
    notes: str | None = None


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(VehicleBase):
    pass


class VehicleResponse(VehicleBase):
    id: int
    # ДОДАНО: Тепер при отриманні авто бекенд віддаватиме ще й масив файлів
    files: list[VehicleFileResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True
