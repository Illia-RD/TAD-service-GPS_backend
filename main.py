from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Імпортуємо моделі, щоб вони зареєструвалися в Base (це важливо для SQLAlchemy)
# Ми звертаємось до них, щоб примусити Python завантажити ці файли
# Імпортуємо наші розділені роутери
from app.api.endpoints import tickets, vehicles

# Імпортуємо базові класи для створення таблиць
from app.core.database import Base, engine

# Створюємо таблиці в БД
Base.metadata.create_all(bind=engine)

app = FastAPI(title="TAD Service GPS API")

# Налаштування CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Підключаємо роутери
# Тепер вони чітко рознесені: /api/vehicles та /api/tickets
app.include_router(vehicles.router, prefix="/api/vehicles", tags=["vehicles"])
app.include_router(tickets.router, prefix="/api/tickets", tags=["tickets"])


@app.get("/api/ping")
def ping():
    return {"status": "ok", "message": "Бекенд працює на ідеальній архітектурі!"}
