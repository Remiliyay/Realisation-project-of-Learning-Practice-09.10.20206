"""
Точка входа приложения "Моя Полка".

При запуске:
1. Инициализирует базу данных (создаёт таблицы при необходимости).
2. Заполняет справочники тестовыми данными, если таблица statuses пуста.
3. Открывает главное окно Tkinter (1100x700).
"""

import os
import sys
import tkinter as tk

# Добавляем папку src в путь для импортов вне зависимости от cwd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import initialize_db, get_connection
from ui.main_window import MainWindow
from ui.theme import apply_light_theme

## Тестовые данные справочников (заполняются только при пустой таблице statuses)
DEFAULT_STATUSES = ["Запланировано", "В процессе", "Завершено"]
DEFAULT_GENRES = ["Фэнтези", "Фантастика", "Классика", "Антиутопия", "Роман"]
DEFAULT_AUTHORS = ["Дж. Р. Р. Толкин", "Фрэнк Герберт", "Фёдор Достоевский",
                   "Джордж Оруэлл", "Станислав Лем", "Михаил Булгаков"]


def seed_reference_data():
    """Заполняет справочники тестовыми данными, если statuses пуста."""
    conn = get_connection()
    try:
        cursor = conn.execute("SELECT COUNT(*) AS cnt FROM statuses")
        if cursor.fetchone()["cnt"] > 0:
            return  # Справочники уже заполнены

        conn.executemany("INSERT INTO statuses (name) VALUES (?)",
                         [(name,) for name in DEFAULT_STATUSES])
        conn.executemany("INSERT INTO genres (name) VALUES (?)",
                         [(name,) for name in DEFAULT_GENRES])
        conn.executemany("INSERT INTO authors (name) VALUES (?)",
                         [(name,) for name in DEFAULT_AUTHORS])
        conn.commit()
        print("[OK] Справочники заполнены тестовыми данными")
    finally:
        conn.close()


def main():
    initialize_db()
    seed_reference_data()

    root = tk.Tk()
    root.title("Моя Полка")
    root.geometry("1100x700")
    root.minsize(900, 560)
    apply_light_theme(root)

    MainWindow(root)

    root.mainloop()


if __name__ == "__main__":
    main()
