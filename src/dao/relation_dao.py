from database import get_connection


class RelationDAO:
    """Работа со связями Many-to-Many."""

    def add_genre(self, item_id, genre_id):
        conn = get_connection()
        try:
            conn.execute(
                "INSERT INTO item_genres (item_id, genre_id) VALUES (?, ?)",
                (item_id, genre_id),
            )
            conn.commit()
        finally:
            conn.close()

    def add_author(self, item_id, author_id):
        conn = get_connection()
        try:
            conn.execute(
                "INSERT INTO item_authors (item_id, author_id) VALUES (?, ?)",
                (item_id, author_id),
            )
            conn.commit()
        finally:
            conn.close()

    def clear_genres(self, item_id):
        """Удалить все жанры у книги (перед обновлением)."""
        conn = get_connection()
        try:
            conn.execute("DELETE FROM item_genres WHERE item_id = ?", (item_id,))
            conn.commit()
        finally:
            conn.close()

    def clear_authors(self, item_id):
        conn = get_connection()
        try:
            conn.execute("DELETE FROM item_authors WHERE item_id = ?", (item_id,))
            conn.commit()
        finally:
            conn.close()
