import csv
import io
import os
import re
from uuid import uuid4

import pandas as pd


def parse_text_content(raw_content: str) -> list[tuple[float, float]]:
    """Логіка для текстових файлів. Повертає відсортований список [(Літри, Код), ...]."""
    points = []

    # 1. Формат IGLA 3D: (Код.Літри)
    igla_matches = re.findall(r"\((\d+)\.(\d+)\)", raw_content)
    if igla_matches and len(igla_matches) > 3:
        return [(float(liters), float(code)) for code, liters in igla_matches]

    # 2. Формат NAVITRACK: Літри:Код (або Літри-Код)
    navitrack_matches = re.findall(
        r"(\d+(?:\.\d+)?)\s*[:|-]\s*(\d+(?:\.\d+)?)", raw_content
    )
    if navitrack_matches and len(navitrack_matches) > 3:
        return [(float(liters), float(code)) for liters, code in navitrack_matches]

    # 3. Формат EPSILON / CSV / TXT: Літри Код
    for line in raw_content.split("\n"):
        line = line.strip()
        if not line:
            continue
        # Шукаємо числа через пробіл, таб, кому або крапку з комою
        match = re.match(r"^(\d+(?:\.\d+)?)[,\t; ]+(\d+(?:\.\d+)?)$", line)
        if match:
            points.append((float(match.group(1)), float(match.group(2))))

    if len(points) >= 3:
        return sorted(points, key=lambda x: x[0])
    return []


def standardize_tare_data(
    content_bytes: bytes, filename: str
) -> list[tuple[float, float]]:
    """Розпізнає розширення файлу і витягує дані."""
    # Якщо це EXCEL
    if filename.lower().endswith((".xls", ".xlsx")):
        try:
            # Читаємо Excel, не звертаючи уваги на заголовки
            df = pd.read_excel(io.BytesIO(content_bytes), header=None)
            points = []

            # Перебираємо рядки. Очікуємо: колонка 0 = Літри, колонка 1 = Код
            for _, row in df.iterrows():
                try:
                    liters = float(row[0])
                    code = float(row[1])
                    points.append((liters, code))
                except (ValueError, TypeError):
                    continue  # Пропускаємо рядки з текстом (заголовки)

            if len(points) >= 3:
                return sorted(points, key=lambda x: x[0])
            return []
        except Exception as e:
            print(f"Помилка парсингу Excel: {e}")
            return []

    # Якщо це звичайний ТЕКСТОВИЙ файл (.csv, .txt, .xml тощо)
    else:
        try:
            raw_content = content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            raw_content = content_bytes.decode("cp1251", errors="ignore")

        return parse_text_content(raw_content)


def process_and_save_tare_file(
    content_bytes: bytes, original_filename: str, upload_dir: str
) -> tuple[str, str]:
    """Створює ідеальний стандартизований CSV (Код,Літри) без заголовків."""

    points = standardize_tare_data(content_bytes, original_filename)
    if not points:
        return None, None

    os.makedirs(upload_dir, exist_ok=True)
    base_name = os.path.splitext(original_filename)[0]

    new_filename = f"{base_name}_standard.csv"
    unique_filename = f"{uuid4().hex[:8]}_{new_filename}"
    file_path = os.path.join(upload_dir, unique_filename)

    # Зберігаємо "чистий" пролив
    with open(file_path, mode="w", encoding="utf-8", newline="") as f:
        # Розділювачем ставимо звичайну кому (якщо треба крапку з комою, зміни delimiter на ";")
        writer = csv.writer(f, delimiter=",")

        # ЗАГОЛОВКІВ НЕМАЄ ВЗАГАЛІ
        for liters, code in points:
            l_val = int(liters) if liters.is_integer() else liters
            c_val = int(code) if code.is_integer() else code

            # Пишемо у форматі: X (Код), Y (Літри)
            writer.writerow([c_val, l_val])

    return file_path.replace("\\", "/"), new_filename
