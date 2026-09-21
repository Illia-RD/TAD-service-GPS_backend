import os
import uuid
from io import BytesIO

from PIL import Image

# Переконайся, що папка існує
PHOTO_UPLOAD_DIR = "uploads/photos"
os.makedirs(PHOTO_UPLOAD_DIR, exist_ok=True)


async def compress_and_save_photo(file_contents: bytes) -> str:
    """
    Приймає байти картинки, стискає її, конвертує у WebP і зберігає на диск.
    Повертає відносний шлях до файлу.
    """
    image = Image.open(BytesIO(file_contents))

    # Виправляємо проблеми з прозорістю, якщо завантажили PNG
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")

    # Максимальний розмір зі збереженням пропорцій
    image.thumbnail((1280, 1280))

    # Генеруємо унікальне ім'я файлу
    file_name = f"tank_{uuid.uuid4().hex}.webp"
    file_path = os.path.join(PHOTO_UPLOAD_DIR, file_name)

    # Зберігаємо (quality=75 - ідеальний баланс ваги і якості для WebP)
    image.save(file_path, "WEBP", quality=75)

    return f"/{file_path}"
