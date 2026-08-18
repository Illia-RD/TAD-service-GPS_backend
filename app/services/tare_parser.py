import csv
import os
import re
from uuid import uuid4


def standardize_tare_data(raw_content: str) -> list[tuple[float, float]]:
    """Парсить текст і повертає відсортований список точок [(Літри, Код), ...]."""
    points = []

    # 1. Формат IGLA 3D: (Код.Літри)
    # Наприклад (2109.20) -> Група 1 = 2109 (Код), Група 2 = 20 (Літри)
    igla_matches = re.findall(r"\((\d+)\.(\d+)\)", raw_content)
    if igla_matches and len(igla_matches) > 3:
        return [(float(liters), float(code)) for code, liters in igla_matches]

    # 2. Формат NAVITRACK: Літри:Код (або Літри-Код)
    navitrack_matches = re.findall(
        r"(\d+(?:\.\d+)?)\s*[:|-]\s*(\d+(?:\.\d+)?)", raw_content
    )
    if navitrack_matches and len(navitrack_matches) > 3:
        return [(float(liters), float(code)) for liters, code in navitrack_matches]

    # 3. Формат EPSILON / CSV / EXCEL: Літри Код
    for line in raw_content.split("\n"):
        line = line.strip()
        if not line:
            continue
        # Шукаємо числа через пробіл, таб, кому або крапку з комою
        match = re.match(r"^(\d+(?:\.\d+)?)[,\t; ]+(\d+(?:\.\d+)?)$", line)
        if match:
            points.append((float(match.group(1)), float(match.group(2))))

    # Якщо знайшли хоча б 3 точки - сортуємо
    if len(points) >= 3:
        return sorted(points, key=lambda x: x[0])

    return []


def process_and_save_tare_file(
    raw_content: str, original_filename: str, upload_dir: str
) -> tuple[str, str]:
    """Створює ідеальний стандартизований CSV і повертає (шлях, нове_імя)."""
    points = standardize_tare_data(raw_content)
    if not points:
        # Якщо нічого не знайшли, повертаємо None
        return None, None

    os.makedirs(upload_dir, exist_ok=True)
    base_name = os.path.splitext(original_filename)[0]

    # Генеруємо назву файлу
    new_filename = f"{base_name}_standard.csv"
    unique_filename = f"{uuid4().hex[:8]}_{new_filename}"
    file_path = os.path.join(upload_dir, unique_filename)

    # Зберігаємо "чистий" пролив
    with open(file_path, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Об'єм (л)", "Код ДВРП"])
        for liters, code in points:
            # int(liters) відкидає .0, якщо число ціле (20.0 -> 20)
            writer.writerow(
                [
                    int(liters) if liters.is_integer() else liters,
                    int(code) if code.is_integer() else code,
                ]
            )

    # Повертаємо нормальні слеші для бази даних
    return file_path.replace("\\", "/"), new_filename
