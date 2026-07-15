from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.models.ticket import PriorityEnum, StatusEnum, TicketGroupEnum


# Схема для однієї задачі (щоб віддавати на фронт)
class TaskSchema(BaseModel):
    id: int
    description: str
    is_completed: bool

    class Config:
        from_attributes = True


class TicketBase(BaseModel):
    vehicle_id: int
    priority: Optional[PriorityEnum] = PriorityEnum.medium
    status: Optional[StatusEnum] = StatusEnum.queue
    ticket_group: TicketGroupEnum
    comment: Optional[str] = None  # Загальний коментар до тікета
    planned_at: Optional[datetime] = None
    creator_id: Optional[int] = None


class TicketCreate(TicketBase):
    tasks: List[str]  # Фронт буде присилати масив: ["Заміна ДВРП", "Тарування"]


class TicketSchema(TicketBase):
    id: int
    title: str  # Згенеруємо автоматично з задач
    created_at: datetime
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    tasks: List[TaskSchema] = []  # Вкладаємо задачі всередину тікета

    class Config:
        from_attributes = True
