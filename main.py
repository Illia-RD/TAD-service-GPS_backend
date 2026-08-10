import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles  # <--- 1. ДОДАНО ІМПОРТ

from app.api.endpoints import dictionaries, tickets, vehicles
from app.core.database import Base, engine

# Створюємо таблиці в БД
Base.metadata.create_all(bind=engine)
os.makedirs("uploads/tare_files", exist_ok=True)
app = FastAPI(title="TAD Service GPS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],  # Дозволяє всі методи (GET, POST, PUT, DELETE тощо)
    allow_headers=["*"],  # Дозволяє всі заголовки
)

# --- 2. ДОДАНО РОЗДАЧУ ФАЙЛІВ ---
# Цей рядок робить папку "uploads" публічною, щоб фронтенд міг завантажити з неї Excel чи TXT
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
# -------------------------------

# Підключаємо роутери
app.include_router(vehicles.router, prefix="/api/vehicles", tags=["vehicles"])
app.include_router(tickets.router, prefix="/api/tickets", tags=["tickets"])
app.include_router(
    dictionaries.router, prefix="/api/dictionaries", tags=["dictionaries"]
)


@app.get("/api/ping")
def ping():
    return {"status": "ok", "message": "Бекенд працює на ідеальній архітектурі!"}
