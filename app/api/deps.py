from app.core.database import SessionLocal


def get_db():
    """
    Видає сесію бази даних для кожного запиту
    і гарантовано її закриває після використання.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
