from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite для швидкого старту
SQLALCHEMY_DATABASE_URL = "sqlite:///./fleet.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Створюємо Base тут, щоб інші моделі могли його імпортувати
Base = declarative_base()

# Залежність для отримання сесії БД в ендпоінтах
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()