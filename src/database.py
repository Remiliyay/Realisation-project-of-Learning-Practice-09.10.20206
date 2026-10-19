import sqlite3
import os

# Путь к файлу БД (будет создан в папке src)
DB_PATH = os.path.join(os.path.dirname(__file__), "collection.db")

# SQL-скрипт создания всех таблиц
CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS statuses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS genres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS authors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    year INTEGER,
    rating REAL,
    status_id INTEGER,
    notes TEXT,
    FOREIGN KEY (status_id) REFERENCES statuses(id)
);

CREATE TABLE IF NOT EXISTS item_genres (
    item_id INTEGER,
    genre_id INTEGER,
    PRIMARY KEY (item_id, genre_id),
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES genres(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS item_authors (
    item_id INTEGER,
    author_id INTEGER,
    PRIMARY KEY (item_id, author_id),
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE
);
"""


def get_connection():
    """Возвращает подключение к БД."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Чтобы получать строки как словари
    conn.execute("PRAGMA foreign_keys = ON")  # Включаем проверку внешних ключей
    return conn


def initialize_db():
    """Создаёт БД и все таблицы, если их ещё нет."""
    conn = get_connection()
    try:
        conn.executescript(CREATE_TABLES_SQL)
        conn.commit()
        print(f"[OK] База данных инициализирована: {DB_PATH}")
    except sqlite3.Error as e:
        print(f"[ERROR] Ошибка инициализации БД: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    initialize_db()
