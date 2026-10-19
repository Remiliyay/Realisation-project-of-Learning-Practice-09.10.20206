from base_dao import BaseDAO
from database import get_connection


class ItemDAO(BaseDAO):
    TABLE_NAME = "items"

    def insert(self, title, year=None, rating=None, status_id=None, notes=None):
        """Добавить новую книгу. Возвращает ID новой записи."""
        conn = self._get_conn()
        try:
            cursor = conn.execute(
                """INSERT INTO items (title, year, rating, status_id, notes)
                   VALUES (?, ?, ?, ?, ?)""",
                (title, year, rating, status_id, notes),
            )
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"[ERROR] Не удалось добавить книгу: {e}")
            return None
        finally:
            conn.close()

    def update(self, item_id, title, year=None, rating=None,
               status_id=None, notes=None):
        """Обновить книгу. Возвращает True при успехе."""
        conn = self._get_conn()
        try:
            cursor = conn.execute(
                """UPDATE items
                   SET title=?, year=?, rating=?, status_id=?, notes=?
                   WHERE id=?""",
                (title, year, rating, status_id, notes, item_id),
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    # ===== Бизнес-запросы =====

    def get_all_with_details(self):
        """Получить все книги с именами статусов, авторов и жанров."""
        conn = self._get_conn()
        try:
            cursor = conn.execute("""
                SELECT
                    i.id,
                    i.title,
                    i.year,
                    i.rating,
                    s.name AS status_name,
                    GROUP_CONCAT(DISTINCT a.name, ', ') AS authors,
                    GROUP_CONCAT(DISTINCT g.name, ', ') AS genres
                FROM items i
                LEFT JOIN statuses s ON i.status_id = s.id
                LEFT JOIN item_authors ia ON i.id = ia.item_id
                LEFT JOIN authors a ON ia.author_id = a.id
                LEFT JOIN item_genres ig ON i.id = ig.item_id
                LEFT JOIN genres g ON ig.genre_id = g.id
                GROUP BY i.id
                ORDER BY i.year DESC
            """)
            return cursor.fetchall()
        finally:
            conn.close()

    def search(self, pattern):
        """Поиск по названию или автору."""
        conn = self._get_conn()
        try:
            search_term = f"%{pattern}%"
            cursor = conn.execute("""
                SELECT DISTINCT i.id, i.title, i.year, i.rating, s.name AS status_name
                FROM items i
                LEFT JOIN statuses s ON i.status_id = s.id
                LEFT JOIN item_authors ia ON i.id = ia.item_id
                LEFT JOIN authors a ON ia.author_id = a.id
                WHERE i.title LIKE ? OR a.name LIKE ?
            """, (search_term, search_term))
            return cursor.fetchall()
        finally:
            conn.close()

    def filter_by_status(self, status_id):
        """Фильтр по статусу, сортировка по оценке."""
        conn = self._get_conn()
        try:
            cursor = conn.execute("""
                SELECT i.id, i.title, i.year, i.rating, s.name AS status_name
                FROM items i
                JOIN statuses s ON i.status_id = s.id
                WHERE i.status_id = ?
                ORDER BY i.rating DESC
            """, (status_id,))
            return cursor.fetchall()
        finally:
            conn.close()

    def get_total_count(self):
        """Общее количество книг."""
        conn = self._get_conn()
        try:
            cursor = conn.execute("SELECT COUNT(*) AS total FROM items")
            row = cursor.fetchone()
            return row["total"] if row else 0
        finally:
            conn.close()

    def get_average_rating(self, status_id=None):
        """Средняя оценка (опционально только для определённого статуса)."""
        conn = self._get_conn()
        try:
            if status_id:
                cursor = conn.execute(
                    "SELECT AVG(rating) AS avg_r FROM items WHERE status_id = ? AND rating IS NOT NULL",
                    (status_id,),
                )
            else:
                cursor = conn.execute(
                    "SELECT AVG(rating) AS avg_r FROM items WHERE rating IS NOT NULL"
                )
            row = cursor.fetchone()
            return round(row["avg_r"], 2) if row and row["avg_r"] else 0
        finally:
            conn.close()

    def get_distribution_by_status(self):
        """Распределение книг по статусам."""
        conn = self._get_conn()
        try:
            cursor = conn.execute("""
                SELECT s.name AS status_name, COUNT(i.id) AS book_count
                FROM statuses s
                LEFT JOIN items i ON s.id = i.status_id
                GROUP BY s.id
                ORDER BY book_count DESC
            """)
            return cursor.fetchall()
        finally:
            conn.close()
