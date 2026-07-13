from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Імпортуємо налаштування БД
from app.core.database import Base, engine, get_db

# Імпортуємо моделі ОБОХ файлів, щоб SQLAlchemy знала про їхнє існування при створенні бази
from app.models import vehicle

# Створюємо таблиці в базі даних (файл fleet.db з'явиться в корені)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="TAD Service GPS API")

# Налаштування CORS для React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Потім тут пропишемо точну адресу фронту
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/ping")
def ping():
    return {"status": "ok", "message": "Backend is running with Layered Architecture!"}


@app.get("/api/vehicles")
def get_vehicles(db: Session = Depends(get_db)):
    # Тепер models розділені, тому звертаємося через модулі
    return db.query(vehicle.Vehicle).all()
