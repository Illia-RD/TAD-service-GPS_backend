from datetime import datetime

from pydantic import BaseModel, Field


# --- ДОПОМІЖНІ МОДЕЛІ ДЛЯ ОБЛАДНАННЯ (Баки і ДРП поки залишаємо як JSON) ---
class TankItem(BaseModel):
    id: str
    tank_model_id: int | None = None
    tank_volume: float | None = None
    actual_volume: float | None = None
    notes: str | None = None
    photo_paths: list[str] = Field(default_factory=list)


class DrpItem(BaseModel):
    id: str
    drp_type: str | None = None
    drp_height: float | None = None
    tank_id: str
    serial_number: str | None = None
    connection_type: str | None = None


# === НОВІ СХЕМИ ДЛЯ СІМ-КАРТ ===
class SimCardBase(BaseModel):
    phone_number: str
    iccid: str | None = None
    operator: str | None = None
    status: str = "new"  # new, active, problematic, deactivated


class SimCardResponse(SimCardBase):
    id: int
    tracker_id: int | None = None

    class Config:
        from_attributes = True


# === НОВІ СХЕМИ ДЛЯ ТРЕКЕРІВ ===
class TrackerBase(BaseModel):
    imei: str
    model: str | None = None
    serial_number: str | None = None
    sent_id: str | None = None  # <--- Додали SENT ID
    status: str = "new"  # new, used, broken, repair, diagnostics


class TrackerResponse(TrackerBase):
    id: int
    vehicle_id: int | None = None
    sim_cards: list[SimCardResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


# === СХЕМА ЛОГІВ (ІСТОРІЇ) ===
class EquipmentLogResponse(BaseModel):
    id: int
    entity_type: str  # 'tracker' або 'sim'
    entity_id: int
    action: str  # 'installed', 'removed', 'status_changed'
    description: str | None = None
    vehicle_id: int | None = None
    created_at: datetime

    class Config:
        from_attributes = True


# --- СХЕМА ДЛЯ ФАЙЛІВ ТАРУВАННЯ ---
class VehicleFileResponse(BaseModel):
    id: int
    vehicle_id: int | None = None
    file_name: str
    file_path: str
    file_type: str | None = "тарування"
    tank_index: int | None = None

    h1: float | None = None
    h2: float | None = None
    no_neck_access: bool | None = False

    is_etalon: bool | None = False
    tank_model_id: int | None = None
    actual_volume: float | None = None
    tank_photo_path: str | None = None
    tank_notes: str | None = None

    class Config:
        from_attributes = True


class VehicleFileUpdate(BaseModel):
    h1: float | None = None
    h2: float | None = None
    no_neck_access: bool | None = None
    vehicle_id: int | None = None
    is_etalon: bool | None = None


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
    status: str | None = "connected"

    tanks_data: list[TankItem] = Field(default_factory=list)
    drps_data: list[DrpItem] = Field(default_factory=list)
    other_equipment: str | None = None
    notes: str | None = None


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(VehicleBase):
    pass


class VehicleResponse(VehicleBase):
    id: int
    files: list[VehicleFileResponse] = Field(default_factory=list)
    # Тепер машина віддає повноцінні об'єкти трекерів з їхніми сімками
    trackers: list[TrackerResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True
