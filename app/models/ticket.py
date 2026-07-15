import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


# ==========================================
# ENUMS & MANY-TO-MANY TABLE
# ==========================================
class RoleEnum(str, enum.Enum):
    admin = "admin"
    manager = "manager"
    mechanic = "mechanic"


class PriorityEnum(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class StatusEnum(str, enum.Enum):
    queue = "queue"
    planned = "planned"
    in_progress = "in_progress"
    done = "done"
    partial = "partial"
    canceled = "canceled"


# ДОДАНО: Енумератор для груп
class TicketGroupEnum(str, enum.Enum):
    gps = "GPS"
    mechanics = "Механіки"
    electricians = "Електрики"
    production = "Виробництво"
    it = "IT"
    auto_electricians = "Автоелектрики"


ticket_assignees = Table(
    "ticket_assignees",
    Base.metadata,
    Column(
        "ticket_id",
        Integer,
        ForeignKey("tickets.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    ),
)


# ==========================================
# MODELS
# ==========================================
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.mechanic)
    telegram_id = Column(String(50), unique=True, nullable=True)
    is_active = Column(Boolean, default=True)

    tickets_created = relationship(
        "Ticket", foreign_keys="Ticket.creator_id", back_populates="creator"
    )
    tickets_assigned = relationship(
        "Ticket", secondary=ticket_assignees, back_populates="assignees"
    )


class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(
        Integer, ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False
    )
    creator_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    title = Column(String(200), nullable=False)
    status = Column(Enum(StatusEnum), default=StatusEnum.queue, index=True)
    priority = Column(Enum(PriorityEnum), default=PriorityEnum.medium)

    # ДОДАНО: Група тікета
    ticket_group = Column(
        Enum(TicketGroupEnum), default=TicketGroupEnum.mechanics, index=True
    )
    comment = Column(Text, nullable=True)
    # Дати (datetime.utcnow автоматично ставить поточний час при створенні)
    created_at = Column(DateTime, default=datetime.utcnow)
    planned_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)

    # Зв'язки
    vehicle = relationship("Vehicle", back_populates="tickets")
    creator = relationship(
        "User", foreign_keys=[creator_id], back_populates="tickets_created"
    )
    assignees = relationship(
        "User", secondary=ticket_assignees, back_populates="tickets_assigned"
    )
    tasks = relationship("Task", back_populates="ticket", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(
        Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False
    )
    category = Column(String(50), nullable=False)
    description = Column(String(255), nullable=False)
    is_completed = Column(Boolean, default=False)
    ticket = relationship("Ticket", back_populates="tasks")


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(
        Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False
    )
    author_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
