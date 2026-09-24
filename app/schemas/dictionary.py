from pydantic import BaseModel, ConfigDict


class DictItemBase(BaseModel):
    name: str


class DictItemCreate(DictItemBase):
    pass


class DictItemResponse(DictItemBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class TankModelBase(BaseModel):
    name: str
    shape_type: str = "rectangular"
    nominal_volume: float | None = None
    dim_l: float | None = None
    dim_w: float | None = None
    dim_h: float | None = None
    step_l: float | None = None
    step_w: float | None = None
    step_h: float | None = None


class TankModelCreate(TankModelBase):
    pass


class TankModelResponse(TankModelBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class CustomFieldTemplateBase(BaseModel):
    department: str
    field_name: str
    field_type: str = "text"
    options: list[str] | None = None
    is_required: bool = False


class CustomFieldTemplateCreate(CustomFieldTemplateBase):
    pass


class CustomFieldTemplateResponse(CustomFieldTemplateBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
