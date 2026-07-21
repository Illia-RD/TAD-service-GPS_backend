from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.ticket import Task, Ticket
from app.schemas.ticket import TaskSchema, TicketCreate, TicketSchema

router = APIRouter()


# Схема для оновлення статусу тікета
class TicketStatusUpdate(BaseModel):
    status: str


class TaskUpdateSchema(BaseModel):
    id: Optional[int] = None  # Якщо id є - оновлюємо, якщо нема - це нова задача
    description: str
    is_completed: bool = False


class TicketUpdateSchema(BaseModel):
    vehicle_id: int
    ticket_group: str
    priority: str
    comment: Optional[str] = None
    planned_at: Optional[datetime] = None
    tasks: List[TaskUpdateSchema]  # Приймаємо повні об'єкти задач


@router.get("/", response_model=list[TicketSchema])
def read_tickets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tickets = db.query(Ticket).offset(skip).limit(limit).all()
    return tickets


@router.post("/", response_model=TicketSchema)
def create_ticket(ticket: TicketCreate, db: Session = Depends(get_db)):
    if not ticket.tasks:
        raise HTTPException(
            status_code=400, detail="Тікет повинен містити хоча б одну задачу"
        )

    # Генеруємо назву тікета з перших задач (для відображення на дошці)
    generated_title = ", ".join(ticket.tasks)[:195]
    if len(generated_title) == 195:
        generated_title += "..."

    # 1. Створюємо сам тікет
    db_ticket = Ticket(
        title=generated_title,
        vehicle_id=ticket.vehicle_id,
        priority=ticket.priority,
        status=ticket.status,
        ticket_group=ticket.ticket_group,
        planned_at=ticket.planned_at,
        creator_id=ticket.creator_id,
        comment=ticket.comment,  # Коментар тепер успішно записується
    )
    db.add(db_ticket)
    db.flush()  # Отримуємо ID тікета, але ще не комітимо остаточно

    # 2. Створюємо задачі і правильно прив'язуємо їх до об'єкта тікета
    for task_desc in ticket.tasks:
        db_task = Task(category="Робота", description=task_desc)
        db_ticket.tasks.append(db_task)  # Прикріплюємо напряму до тікета!

    # 3. Зберігаємо все разом
    db.commit()
    db.refresh(db_ticket)
    return db_ticket


@router.patch("/{ticket_id}/status", response_model=TicketSchema)
def update_ticket_status(
    ticket_id: int, status_update: TicketStatusUpdate, db: Session = Depends(get_db)
):
    """Оновлює колонку/статус тікета на дошці з логікою часткового закриття"""
    db_ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Тікет не знайдено")

    old_status = db_ticket.status
    new_status = status_update.status

    # 1. Фіксуємо дати
    if new_status == "in_progress" and old_status != "in_progress":
        db_ticket.started_at = datetime.utcnow()
    elif new_status == "done" and old_status != "done":
        db_ticket.finished_at = datetime.utcnow()

    # 2. Логіка ЧАСТКОВОГО ВИКОНАННЯ (Перенесення залишків)
    if new_status == "done":
        uncompleted_tasks = [t for t in db_ticket.tasks if not t.is_completed]

        if uncompleted_tasks:
            # Генеруємо назву для нового тікета з невиконаних задач
            new_title = ", ".join([t.description for t in uncompleted_tasks])[:195]

            # Створюємо новий тікет для залишку
            new_ticket = Ticket(
                title=new_title,
                vehicle_id=db_ticket.vehicle_id,
                priority=db_ticket.priority,
                status="queue",  # Кидаємо знову в чергу
                ticket_group=db_ticket.ticket_group,
                creator_id=db_ticket.creator_id,
                comment=f"[АВТОМАТИЧНО СТВОРЕНО: Залишок робіт від тікета #{db_ticket.id}]\n\n{db_ticket.comment or ''}",
            )
            db.add(new_ticket)
            db.flush()  # Отримуємо ID нового тікета

            # Переміщуємо невиконані задачі в новий тікет
            for task in uncompleted_tasks:
                task.ticket_id = new_ticket.id

    db_ticket.status = new_status
    db.commit()
    db.refresh(db_ticket)
    return db_ticket


@router.patch("/tasks/{task_id}/toggle", response_model=TaskSchema)
def toggle_task(task_id: int, db: Session = Depends(get_db)):
    """Перемикає стан виконання конкретної задачі (чекбокс)"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задачу не знайдено")

    task.is_completed = not task.is_completed  # Міняємо статус на протилежний
    db.commit()
    db.refresh(task)
    return task


@router.put("/{ticket_id}", response_model=TicketSchema)
def update_ticket_full(
    ticket_id: int, ticket_data: TicketUpdateSchema, db: Session = Depends(get_db)
):
    """Повноцінне оновлення тікета разом із синхронізацією задач"""
    db_ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Тікет не знайдено")

    # 1. Оновлюємо "шапку" тікета
    db_ticket.vehicle_id = ticket_data.vehicle_id
    db_ticket.ticket_group = ticket_data.ticket_group
    db_ticket.priority = ticket_data.priority
    db_ticket.comment = ticket_data.comment
    db_ticket.planned_at = ticket_data.planned_at

    # 2. Синхронізуємо задачі
    existing_tasks = {task.id: task for task in db_ticket.tasks}
    incoming_ids = [t.id for t in ticket_data.tasks if t.id is not None]

    # А) Видаляємо ті, що були в БД, але юзер їх видалив з форми
    for task_id, task in existing_tasks.items():
        if task_id not in incoming_ids:
            db.delete(task)

    # Б) Оновлюємо існуючі або додаємо абсолютно нові
    for t_data in ticket_data.tasks:
        if t_data.id and t_data.id in existing_tasks:
            # Оновлюємо існуючу
            existing_task = existing_tasks[t_data.id]
            existing_task.description = t_data.description
            existing_task.is_completed = t_data.is_completed
        else:
            # Створюємо нову
            new_task = Task(
                category="Робота",
                description=t_data.description,
                is_completed=t_data.is_completed,
            )
            db_ticket.tasks.append(new_task)

    db.commit()
    db.refresh(db_ticket)
    return db_ticket
