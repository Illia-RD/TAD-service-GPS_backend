from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.ticket import PriorityEnum, StatusEnum, TicketGroupEnum


class TaskBase(BaseModel):
    description: str
    is_completed: bool = False


class TaskCreate(TaskBase):
    pass


class TaskResponse(TaskBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class TicketBase(BaseModel):
    vehicle_id: int
    priority: PriorityEnum = PriorityEnum.medium
    status: StatusEnum = StatusEnum.queue
    ticket_group: TicketGroupEnum = TicketGroupEnum.mechanics
    comment: str | None = None
    planned_at: datetime | None = None
    creator_id: int | None = None


class TicketCreate(TicketBase):
    tasks: list[str] = []  # Фронт присилає масив рядків для створення


class TicketResponse(TicketBase):
    id: int
    title: str
    created_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None
    tasks: list[TaskResponse] = []
    model_config = ConfigDict(from_attributes=True)
