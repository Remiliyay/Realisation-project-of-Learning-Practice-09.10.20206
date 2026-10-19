from base_dao import BaseDAO
from database import get_connection


class StatusDAO(BaseDAO):
    TABLE_NAME = "statuses"

    def insert(self, name):
        conn = self._get_conn()
        try:
            cursor = conn.execute(
                "INSERT INTO statuses (name) VALUES (?)", (name,)
            )
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"[ERROR] Не удалось добавить статус: {e}")
            return None
        finally:
            conn.close()


class GenreDAO(BaseDAO):
    TABLE_NAME = "genres"

    def insert(self, name):
        conn = self._get_conn()
        try:
            cursor = conn.execute(
                "INSERT INTO genres (name) VALUES (?)", (name,)
            )
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"[ERROR] Не удалось добавить жанр: {e}")
            return None
        finally:
            conn.close()


class AuthorDAO(BaseDAO):
    TABLE_NAME = "authors"

    def insert(self, name):
        conn = self._get_conn()
        try:
            cursor = conn.execute(
                "INSERT INTO authors (name) VALUES (?)", (name,)
            )
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"[ERROR] Не удалось добавить автора: {e}")
            return None
        finally:
            conn.close()
