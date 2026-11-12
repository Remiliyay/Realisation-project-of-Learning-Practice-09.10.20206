##
# @file database.py
# @brief Модуль подключения к базе данных SQLite и инициализации схемы БД.
# 
# Этот модуль предоставляет базовую инфраструктуру для работы с локальной 
# базой данных приложения "Моя Полка" (MyShelf). Он отвечает за:
# - Создание файла БД при первом запуске
# - Предоставление функции подключения с настроенными параметрами
# - Инициализацию всех таблиц из встроенного SQL-скрипта
#
# @note База данных хранится локально в папке с исходным кодом (файл collection.db).
#       Сетевые подключения не используются.
#
# @author -
# @version -
# @since 2026-11-12
#
# @see ItemDAO
# @see StatusDAO
# @see GenreDAO
# @see AuthorDAO

import sqlite3
import os

## Путь к файлу БД (создаётся в папке src)
DB_PATH = os.path.join(os.path.dirname(__file__), "collection.db")

## 
# SQL-скрипт создания всех таблиц базы данных.
#
# Создаёт следующие таблицы:
# - @c statuses — справочник статусов чтения
# - @c genres — справочник жанров
# - @c authors — справочник авторов
# - @c items — основная таблица книг
# - @c item_genres — связь M:N между книгами и жанрами
# - @c item_authors — связь M:N между книгами и авторами
#
# @note Используются ограничения внешнего ключа с каскадным удалением
#       (ON DELETE CASCADE) для промежуточных таблиц связей.
#
# @see initialize_db()
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

##
# @brief Возвращает новое подключение к базе данных SQLite.
#
# Создаёт подключение к файлу БД с настроенными параметрами:
# - @c row_factory = sqlite3.Row — для доступа к полям по имени (как словарь)
# - Включена проверка внешних ключей (PRAGMA foreign_keys = ON)
#
# @return Объект подключения sqlite3.Connection
#
# @note Подключение не закрывается автоматически — вызывающий код обязан
#       закрыть его после использования (через conn.close() или контекстный менеджер).
#
# @warning При каждом вызове создаётся НОВОЕ подключение. Для многократных
#          операций в одной функции лучше сохранить подключение в переменную.
#
# @see initialize_db()
def get_connection():
    """Возвращает подключение к БД."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Чтобы получать строки как словари
    conn.execute("PRAGMA foreign_keys = ON")  # Включаем проверку внешних ключей
    return conn

##
# @brief Создаёт базу данных и все таблицы, если их ещё нет.
#
# Выполняет SQL-скрипт CREATE_TABLES_SQL для инициализации схемы БД.
# Если таблицы уже существуют (благодаря IF NOT EXISTS), скрипт не вызывает ошибок.
#
# @note Функция безопасна для многократного вызова — можно запускать при каждом
#       старте приложения без риска потери данных.
#
# @warning В случае ошибки подключения или выполнения SQL скрипт выводит сообщение
#          об ошибке в консоль, но не выбрасывает исключение (fail-soft стратегия).
#
# @see get_connection()
# @see CREATE_TABLES_SQL
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
