from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.models.ticket import PriorityEnum, StatusEnum

# Схема для підзадач (чекліста)
class TaskBase(BaseModel):
    category: str
    description: str
    is_completed: bool = False

class TaskSchema(TaskBase):
    id: int
    ticket_id: int
    
    class Config:
        from_attributes = True

# Схема для самого тікета
class TicketBase(BaseModel):
    vehicle_id: int
    title: str
    priority: PriorityEnum

class TicketSchema(TicketBase):
    id: int
    status: StatusEnum
    created_at: datetime
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    tasks: List[TaskSchema] = []
    
    class Config:
        from_attributes = True