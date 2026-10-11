PRAGMA foreign_keys = ON;

-- =============================================================================
-- 1. Удаление таблиц (если они уже существуют)
-- Порядок важен: сначала удаляем зависимые таблицы, затем основные
-- =============================================================================
DROP TABLE IF EXISTS item_authors;
DROP TABLE IF EXISTS item_genres;
DROP TABLE IF EXISTS items;
DROP TABLE IF EXISTS authors;
DROP TABLE IF EXISTS genres;
DROP TABLE IF EXISTS statuses;

-- =============================================================================
-- 2. Создание справочных таблиц
-- =============================================================================

-- Таблица статусов чтения
CREATE TABLE statuses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL CHECK(length(name) > 0)
);

-- Таблица жанров
CREATE TABLE genres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL CHECK(length(name) > 0)
);

-- Таблица авторов
CREATE TABLE authors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL CHECK(length(name) > 0)
);

-- =============================================================================
-- 3. Создание основной таблицы (Книги)
-- =============================================================================
CREATE TABLE items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL CHECK(length(title) > 0),
    year INTEGER CHECK(year >= 1000 AND year <= 2100),
    rating REAL CHECK(rating >= 1 AND rating <= 10),
    status_id INTEGER,
    notes TEXT,
    -- Связь 1:N со статусами. Если статус удалят, у книги статус станет NULL
    FOREIGN KEY (status_id) REFERENCES statuses(id) ON DELETE SET NULL
);

-- =============================================================================
-- 4. Создание промежуточных таблиц для связей M:N
-- =============================================================================

-- Связь Книга <-> Жанры
CREATE TABLE item_genres (
    item_id INTEGER NOT NULL,
    genre_id INTEGER NOT NULL,
    PRIMARY KEY (item_id, genre_id),
    -- Если удаляем книгу, удаляем и её связи с жанрами (CASCADE)
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
    -- Если удаляем жанр, запрещаем удаление, если он используется (RESTRICT)
    FOREIGN KEY (genre_id) REFERENCES genres(id) ON DELETE RESTRICT
);

-- Связь Книга <-> Авторы
CREATE TABLE item_authors (
    item_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    PRIMARY KEY (item_id, author_id),
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE RESTRICT
);

-- =============================================================================
-- 5. Создание индексов для ускорения поиска и сортировки
-- =============================================================================
-- Индекс для быстрого поиска по названию книги (используется в LIKE '%...%')
CREATE INDEX idx_items_title ON items(title);

-- Индекс для быстрой фильтрации по статусу
CREATE INDEX idx_items_status ON items(status_id);

-- Индексы для сортировки по году и оценке
CREATE INDEX idx_items_year ON items(year);
CREATE INDEX idx_items_rating ON items(rating);
