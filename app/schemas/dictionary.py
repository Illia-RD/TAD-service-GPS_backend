from pydantic import BaseModel


class DictItemBase(BaseModel):
    name: str


class DictItemCreate(DictItemBase):
    pass


class DictItemResponse(DictItemBase):
    id: int

    class Config:
        from_attributes = True
