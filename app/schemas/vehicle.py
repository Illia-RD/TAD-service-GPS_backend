from pydantic import BaseModel, Field


# --- ДОПОМІЖНІ МОДЕЛІ ДЛЯ ОБЛАДНАННЯ ---
class TankItem(BaseModel):
    id: str
    tank_model_id: int | None = None  # <--- ПРИВ'ЯЗКА ДО ДОВІДНИКА
    tank_volume: float | None = None  # Паспортний об'єм
    actual_volume: float | None = None  # Фактичний об'єм
    notes: str | None = None  # <--- ПРИМІТКА (зам'ятий, зміщено ДРП)
    photo_path: str | None = None  # <--- ФОТО конкретного бака на авто


class DrpItem(BaseModel):
    id: str
    drp_type: str | None = None
    drp_height: float | None = None
    tank_id: str
    serial_number: str | None = None
    connection_type: str | None = None


class TrackerItem(BaseModel):
    id: str
    tracker_model: str | None = None
    tracker_imei: str | None = None
    tracker_serial: str | None = None
    sim_operator: str | None = None
    sim_number: str | None = None
    installation_location: str | None = None


# --- СХЕМА ДЛЯ ФАЙЛІВ ТАРУВАННЯ ---
class VehicleFileResponse(BaseModel):
    id: int
    vehicle_id: int | None = None  # <--- ЯКЩО NULL, ТО ФАЙЛ В АРХІВІ (РЕЗЕРВ)
    file_name: str
    file_path: str
    file_type: str | None = "тарування"
    tank_index: int | None = None

    # Дані лінійки
    h1: float | None = None
    h2: float | None = None
    no_neck_access: bool | None = False

    # === АРХІВНІ ДАНІ (ЗЛІПОК) ===
    is_etalon: bool | None = False  # <--- Зірочка "Еталонний файл"
    tank_model_id: int | None = None  # Якому типу бака належить
    actual_volume: float | None = None
    tank_photo_path: str | None = None
    tank_notes: str | None = None

    class Config:
        from_attributes = True


class VehicleFileUpdate(BaseModel):
    h1: float | None = None
    h2: float | None = None
    no_neck_access: bool | None = None
    vehicle_id: int | None = None  # Щоб можна було відв'язати від авто
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

    trackers_data: list[TrackerItem] = Field(default_factory=list)
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

    class Config:
        from_attributes = True
