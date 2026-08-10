from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Імпортуємо моделі, щоб вони зареєструвалися в Base (це важливо для SQLAlchemy)
# Ми звертаємось до них, щоб примусити Python завантажити ці файли
# Імпортуємо наші розділені роутери
from app.api.endpoints import dictionaries, tickets, vehicles

# Імпортуємо базові класи для створення таблиць
from app.core.database import Base, engine

# Створюємо таблиці в БД
Base.metadata.create_all(bind=engine)

app = FastAPI(title="TAD Service GPS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],  # Дозволяє всі методи (GET, POST, PUT, DELETE тощо)
    allow_headers=["*"],  # Дозволяє всі заголовки
)

# Підключаємо роутери
app.include_router(vehicles.router, prefix="/api/vehicles", tags=["vehicles"])
app.include_router(tickets.router, prefix="/api/tickets", tags=["tickets"])
app.include_router(
    dictionaries.router, prefix="/api/dictionaries", tags=["dictionaries"]
)


@app.get("/api/ping")
def ping():
    return {"status": "ok", "message": "Бекенд працює на ідеальній архітектурі!"}
