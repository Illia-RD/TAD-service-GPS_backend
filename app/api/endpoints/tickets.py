from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_db
from app.models.ticket import StatusEnum, Ticket
from app.schemas.ticket import TicketSchema

# Створюємо роутер для тікетів
router = APIRouter()


@router.get("/", response_model=List[TicketSchema])
def get_tickets(db: Session = Depends(get_db)):
    """Отримати всі тікети разом із їхніми підзадачами"""
    # joinedload витягує зв'язані підзадачі одним запитом, щоб не навантажувати БД
    return db.query(Ticket).options(joinedload(Ticket.tasks)).all()


@router.put("/{ticket_id}/status")
def update_ticket_status(
    ticket_id: int, status: StatusEnum, db: Session = Depends(get_db)
):
    """Оновлення статусу тікета при перетягуванні на Kanban-дошці"""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket.status = status

    # Автоматично ставимо час початку або завершення
    if status == StatusEnum.in_progress and not ticket.started_at:
        ticket.started_at = datetime.now()
    elif status == StatusEnum.done:
        ticket.finished_at = datetime.now()

    db.commit()
    return {"status": "success"}


# Додай це у свій файл app/api/endpoints/tickets.py
@router.post("/seed")
def seed_data(db: Session = Depends(get_db)):
    """Тимчасовий метод для створення тестових даних"""
    from app.models.ticket import Ticket

    if db.query(Ticket).first():
        return {"message": "Дані вже є"}

    new_ticket = Ticket(vehicle_id=1, title="Перший тестовий тікет", status="queue")
    db.add(new_ticket)
    db.commit()
    return {"message": "Тестовий тікет створено!"}
