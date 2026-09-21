import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1 import dictionaries, equipment, tickets, vehicles
from app.core.config import settings
from app.core.database import Base, engine

# Створюємо таблиці в БД автоматично при старті (поки без Alembic міграцій)
Base.metadata.create_all(bind=engine)

# Створюємо папки для статики, якщо їх немає
os.makedirs("uploads/photos", exist_ok=True)
os.makedirs("uploads/tare_files", exist_ok=True)

app = FastAPI(title=settings.PROJECT_NAME)

# Налаштування CORS (щоб фронт на React міг стукати сюди)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Монтуємо папку для роздачі фотографій та файлів
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Підключаємо наші роутери
app.include_router(
    dictionaries.router, prefix="/api/dictionaries", tags=["Dictionaries"]
)
app.include_router(vehicles.router, prefix="/api/vehicles", tags=["Vehicles"])
app.include_router(equipment.router, prefix="/api/equipment", tags=["Equipment"])
app.include_router(tickets.router, prefix="/api/tickets", tags=["Tickets"])
