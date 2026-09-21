import os


class Settings:
    PROJECT_NAME: str = "TAD Service GPS"
    # Для продакшену потім змінимо на PostgreSQL, поки лишаємо SQLite
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "sqlite:///./fleet.db")

    # Налаштування CORS
    BACKEND_CORS_ORIGINS: list[str] = ["*"]


settings = Settings()
