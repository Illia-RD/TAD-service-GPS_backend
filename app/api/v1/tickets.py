from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.api.dependencies import DbSession
from app.models.ticket import Task, Ticket
from app.schemas.ticket import TicketCreate, TicketResponse

router = APIRouter()


class TicketStatusUpdate(BaseModel):
    status: str


@router.get("/", response_model=list[TicketResponse])
def get_tickets(db: DbSession):
    return db.query(Ticket).all()


@router.post("/", response_model=TicketResponse)
def create_ticket(ticket_in: TicketCreate, db: DbSession):
    if not ticket_in.tasks:
        raise HTTPException(
            status_code=400, detail="Тікет повинен містити хоча б одну задачу"
        )

    # Генеруємо назву тікета з перших задач (для відображення на дошці)
    generated_title = ", ".join(ticket_in.tasks)[:195]
    if len(generated_title) == 195:
        generated_title += "..."

    ticket_data = ticket_in.model_dump(exclude={"tasks"})
    db_ticket = Ticket(**ticket_data, title=generated_title)
    db.add(db_ticket)
    db.flush()  # Отримуємо ID тікета для задач

    for task_desc in ticket_in.tasks:
        db_task = Task(category="Робота", description=task_desc, ticket_id=db_ticket.id)
        db.add(db_task)

    db.commit()
    db.refresh(db_ticket)
    return db_ticket


@router.patch("/{ticket_id}/status", response_model=TicketResponse)
def update_status(ticket_id: int, status_update: TicketStatusUpdate, db: DbSession):
    db_ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Тікет не знайдено")

    old_status = db_ticket.status
    new_status = status_update.status

    # Фіксуємо час виконання
    if new_status == "in_progress" and old_status != "in_progress":
        db_ticket.started_at = datetime.utcnow()
    elif new_status == "done" and old_status != "done":
        db_ticket.finished_at = datetime.utcnow()

    db_ticket.status = new_status
    db.commit()
    db.refresh(db_ticket)
    return db_ticket


@router.patch("/tasks/{task_id}/toggle")
def toggle_task(task_id: int, db: DbSession):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задачу не знайдено")

    task.is_completed = not task.is_completed
    db.commit()
    return {"id": task.id, "is_completed": task.is_completed}
