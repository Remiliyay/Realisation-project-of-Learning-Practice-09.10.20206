"""
Сервис для работы с книгами (бизнес-логика).
Операции: добавление, редактирование, удаление, поиск/фильтрация.
"""

from dao.item_dao import ItemDAO
from dao.relation_dao import RelationDAO
from dao.reference_dao import StatusDAO, GenreDAO, AuthorDAO


class BookService:
    """Сервис для управления книгами коллекции."""

    def __init__(self):
        self.item_dao = ItemDAO()
        self.relation_dao = RelationDAO()
        self.status_dao = StatusDAO()
        self.genre_dao = GenreDAO()
        self.author_dao = AuthorDAO()

    def add_book(self, title, year=None, rating=None, status_id=None,
                 notes=None, genre_ids=None, author_ids=None):
        """
        Операция 1: Добавление новой книги в коллекцию.
        
        Входные данные:
            title (str) — название книги (обязательное)
            year (int, опционально) — год издания
            rating (float, опционально) — оценка от 1 до 10
            status_id (int) — ID статуса из справочника
            notes (str, опционально) — заметки
            genre_ids (list[int]) — список ID жанров
            author_ids (list[int]) — список ID авторов
        
        Результат:
            int — ID созданной книги (при успехе)
        
        Исключения:
            ValueError — при некорректных входных данных
            RuntimeError — при ошибке БД
        """
        # Валидация входных данных
        self._validate_title(title)
        self._validate_rating(rating)
        self._validate_year(year)
        
        if genre_ids is None:
            genre_ids = []
        if author_ids is None:
            author_ids = []

        try:
            # Шаг 1: Создание книги
            item_id = self.item_dao.insert(title, year, rating, status_id, notes)
            if item_id is None:
                raise RuntimeError("Не удалось сохранить книгу в базу данных")

            # Шаг 2: Привязка жанров
            for genre_id in genre_ids:
                self.relation_dao.add_genre(item_id, genre_id)

            # Шаг 3: Привязка авторов
            for author_id in author_ids:
                self.relation_dao.add_author(item_id, author_id)

            return item_id

        except Exception as e:
            raise RuntimeError(f"Ошибка при добавлении книги: {e}")

    def update_book(self, item_id, title, year=None, rating=None,
                    status_id=None, notes=None, genre_ids=None, author_ids=None):
        """
        Операция 2: Редактирование существующей книги.
        
        Входные данные:
            item_id (int) — ID редактируемой книги
            Остальные поля — как в add_book
        
        Результат:
            bool — True при успехе
        
        Исключения:
            ValueError — при некорректных данных
            RuntimeError — при ошибке БД или отсутствии книги
        """
        # Проверка существования книги
        existing = self.item_dao.get_by_id(item_id)
        if existing is None:
            raise RuntimeError(f"Книга с ID {item_id} не найдена")

        # Валидация
        self._validate_title(title)
        self._validate_rating(rating)
        self._validate_year(year)

        if genre_ids is None:
            genre_ids = []
        if author_ids is None:
            author_ids = []

        try:
            # Шаг 1: Обновление основных полей
            success = self.item_dao.update(item_id, title, year, rating, status_id, notes)
            if not success:
                raise RuntimeError("Не удалось обновить книгу")

            # Шаг 2: Полная перезапись связей
            self.relation_dao.clear_genres(item_id)
            self.relation_dao.clear_authors(item_id)

            for genre_id in genre_ids:
                self.relation_dao.add_genre(item_id, genre_id)

            for author_id in author_ids:
                self.relation_dao.add_author(item_id, author_id)

            return True

        except Exception as e:
            raise RuntimeError(f"Ошибка при редактировании книги: {e}")

    def delete_book(self, item_id):
        """
        Операция 3: Удаление книги с подтверждением.
        
        Входные данные:
            item_id (int) — ID книги
        
        Результат:
            bool — True при успехе
        
        Исключения:
            RuntimeError — при отсутствии книги или ошибке БД
        """
        # Проверка существования
        existing = self.item_dao.get_by_id(item_id)
        if existing is None:
            raise RuntimeError(f"Книга с ID {item_id} не найдена")

        try:
            # ON DELETE CASCADE в БД автоматически удалит связи
            success = self.item_dao.delete(item_id)
            if not success:
                raise RuntimeError("Не удалось удалить книгу")
            return True

        except Exception as e:
            raise RuntimeError(f"Ошибка при удалении книги: {e}")

    def search_and_filter(self, search_query=None, status_id=None,
                          sort_by="year", sort_order="desc"):
        """
        Операция 4: Поиск и фильтрация (комбинированный запрос).
        
        Входные данные:
            search_query (str, опционально) — текст поиска
            status_id (int, опционально) — фильтр по статусу
            sort_by (str) — "year" или "rating"
            sort_order (str) — "asc" или "desc"
        
        Результат:
            list[dict] — список книг
        
        Исключения:
            ValueError — при некорректных параметрах сортировки
        """
        # Валидация сортировки (защита от SQL-инъекций)
        if sort_by not in ["year", "rating", "title"]:
            raise ValueError(f"Недопустимое поле сортировки: {sort_by}. Допустимые: year, rating, title")
        if sort_order not in ["asc", "desc"]:
            raise ValueError(f"Недопустимый порядок сортировки: {sort_order}. Допустимые: asc, desc")

        # Если ничего не выбрано — вернуть все книги
        if search_query is None and status_id is None:
            return self.item_dao.get_all_with_details()

        # Формирование условий
        conditions = []
        params = []

        if search_query is not None:
            pattern = f"%{search_query}%"
            conditions.append("(i.title LIKE ? OR a.name LIKE ?)")
            params.extend([pattern, pattern])

        if status_id is not None:
            conditions.append("i.status_id = ?")
            params.append(status_id)

        # Сборка WHERE
        where_clause = " AND ".join(conditions)

        # Выполнение запроса
        return self.item_dao.search_with_filters(where_clause, params, sort_by, sort_order)

    # ===== Методы для слоя UI =====

    def get_statuses(self):
        """Справочник статусов (для ComboBox / фильтра)."""
        return self.status_dao.get_all()

    def get_genres(self):
        """Справочник жанров (для Listbox выбора)."""
        return self.genre_dao.get_all()

    def get_authors(self):
        """Справочник авторов (для Listbox выбора)."""
        return self.author_dao.get_all()

    def get_book_for_edit(self, item_id):
        """
        Данные книги для предзаполнения окна редактирования.

        Результат:
            tuple — (книга (sqlite3.Row), список genre_ids, список author_ids)

        Исключения:
            RuntimeError — если книга не найдена
        """
        book = self.item_dao.get_by_id(item_id)
        if book is None:
            raise RuntimeError(f"Книга с ID {item_id} не найдена")
        genre_ids = self.relation_dao.get_genre_ids(item_id)
        author_ids = self.relation_dao.get_author_ids(item_id)
        return book, genre_ids, author_ids

    # ===== Вспомогательные методы валидации =====

    def _validate_title(self, title):
        """Проверка названия книги."""
        if title is None or not isinstance(title, str):
            raise ValueError("Название книги должно быть строкой")
        if len(title.strip()) == 0:
            raise ValueError("Поле 'Название' обязательно для заполнения")
        if len(title) > 200:
            raise ValueError("Название книги не должно превышать 200 символов")

    def _validate_rating(self, rating):
        """Проверка оценки."""
        if rating is None:
            return  # Оценка опциональна
        if not isinstance(rating, (int, float)):
            raise ValueError("Оценка должна быть числом")
        if rating < 1 or rating > 10:
            raise ValueError("Оценка должна быть от 1 до 10")

    def _validate_year(self, year):
        """Проверка года издания."""
        if year is None:
            return  # Год опционален
        if not isinstance(year, int):
            raise ValueError("Год издания должен быть целым числом")
        if year < 1000 or year > 2100:
            raise ValueError("Некорректный год издания (допустимо 1000-2100)")
