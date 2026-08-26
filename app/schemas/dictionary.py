from pydantic import BaseModel


class DictItemBase(BaseModel):
    name: str


class DictItemCreate(DictItemBase):
    pass


class DictItemResponse(DictItemBase):
    id: int

    class Config:
        from_attributes = True


# === НОВЕ: ДОВІДНИК ТИПІВ БАКІВ (КАТАЛОГ) ===
class TankModelBase(BaseModel):
    name: str  # напр. "DAF XF 105 Алюміній Сходинка Права"
    shape_type: str = "rectangular"  # rectangular, step_1, step_2, cylinder, custom
    nominal_volume: float | None = None

    # Основні габарити
    dim_l: float | None = None
    dim_w: float | None = None
    dim_h: float | None = None

    # Габарити вирізу/сходинки (якщо є)
    step_l: float | None = None
    step_w: float | None = None
    step_h: float | None = None


class TankModelCreate(TankModelBase):
    pass


class TankModelResponse(TankModelBase):
    id: int

    class Config:
        from_attributes = True
