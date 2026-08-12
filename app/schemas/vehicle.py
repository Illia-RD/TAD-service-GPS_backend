from pydantic import BaseModel, Field

# --- ДОПОМІЖНІ МОДЕЛІ ДЛЯ ОБЛАДНАННЯ ---


class TankItem(BaseModel):
    id: str
    tank_volume: float | None = None
    actual_volume: float | None = None  # <--- ДОДАЛИ ФАКТИЧНИЙ ОБ'ЄМ
    tank_dimensions: str | None = None


class DrpItem(BaseModel):
    id: str
    drp_type: str | None = None
    drp_height: float | None = None
    tank_id: str
    serial_number: str | None = None  # СЕРІЙНИК ДВРП
    connection_type: str | None = None  # ТИП ПІДКЛЮЧЕННЯ


class TrackerItem(BaseModel):
    id: str
    tracker_model: str | None = None
    tracker_imei: str | None = None  # IMEI
    tracker_serial: str | None = None  # СЕРІЙНИК ТРЕКЕРА
    sim_operator: str | None = None
    sim_number: str | None = None
    installation_location: str | None = None  # МІСЦЕ ВСТАНОВЛЕННЯ


# --- СХЕМА ДЛЯ ФАЙЛІВ ТАРУВАННЯ ---
class VehicleFileResponse(BaseModel):
    id: int
    file_name: str
    file_path: str
    file_type: str | None = "тарування"
    tank_index: int | None = (
        None  # <--- ДОДАЛИ ІНДЕКС БАКУ, ЩОБ ФАЙЛ НЕГУБИВСЯ ПРИ ПЕРЕЗАВАНТАЖЕННІ
    )

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
    status: str | None = "connected"  # СТАТУС

    trackers_data: list[TrackerItem] = Field(default_factory=list)
    tanks_data: list[TankItem] = Field(default_factory=list)
    drps_data: list[DrpItem] = Field(default_factory=list)
    other_equipment: str | None = None  # ІНШЕ ОБЛАДНАННЯ
    notes: str | None = None


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(VehicleBase):
    pass


class VehicleResponse(VehicleBase):
    id: int
    files: list[VehicleFileResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True
