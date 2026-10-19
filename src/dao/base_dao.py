from database import get_connection


class BaseDAO:
    """Базовый DAO с общими CRUD-методами."""

    TABLE_NAME = None  # Переопределяется в наследниках

    def _get_conn(self):
        return get_connection()

    def get_all(self):
        """Получить все записи из таблицы."""
        conn = self._get_conn()
        try:
            cursor = conn.execute(f"SELECT * FROM {self.TABLE_NAME}")
            return cursor.fetchall()
        finally:
            conn.close()

    def get_by_id(self, item_id):
        """Получить одну запись по ID."""
        conn = self._get_conn()
        try:
            cursor = conn.execute(
                f"SELECT * FROM {self.TABLE_NAME} WHERE id = ?", (item_id,)
            )
            return cursor.fetchone()
        finally:
            conn.close()

    def delete(self, item_id):
        """Удалить запись по ID. Возвращает True, если удалено."""
        conn = self._get_conn()
        try:
            cursor = conn.execute(
                f"DELETE FROM {self.TABLE_NAME} WHERE id = ?", (item_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
