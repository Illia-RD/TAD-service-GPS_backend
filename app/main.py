import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1 import dictionaries, equipment, tickets, vehicles
from app.core.config import settings
from app.core.database import Base, engine

# 1. ОБОВ'ЯЗКОВО ІМПОРТУЄМО МОДЕЛІ СЮДИ (щоб Base про них дізнався)

# 2. ТЕПЕР СТВОРЮЄМО ТАБЛИЦІ
Base.metadata.create_all(bind=engine)

os.makedirs("uploads/photos", exist_ok=True)
os.makedirs("uploads/tare_files", exist_ok=True)

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(
    dictionaries.router, prefix="/api/v1/dictionaries", tags=["Dictionaries"]
)
app.include_router(vehicles.router, prefix="/api/v1/vehicles", tags=["Vehicles"])
app.include_router(equipment.router, prefix="/api/v1/equipment", tags=["Equipment"])
app.include_router(tickets.router, prefix="/api/v1/tickets", tags=["Tickets"])
