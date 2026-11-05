"""
Консольные тесты для слоя бизнес-логики (Service Layer).
Проверяет все 5 операций из SERVICE_DESIGN.md.
"""

import sys
import os

# Добавляем папку src в путь для импортов
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import initialize_db
from services.book_service import BookService
from services.analytics_service import AnalyticsService


def print_separator(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)


def print_success(message):
    print(f"  SUCCESS {message}")


def print_error(message):
    print(f"  FAILURE {message}")


def test_add_book():
    """Тест операции 1: Добавление книги."""
    print_separator("Тест 1: Добавление книги")
    service = BookService()

    # Тест 1.1: Успешное добавление
    try:
        book_id = service.add_book(
            title="Тестовая книга",
            year=2020,
            rating=8.5,
            status_id=1,
            notes="Тестовая заметка",
            genre_ids=[1],
            author_ids=[1]
        )
        print_success(f"Книга добавлена с ID: {book_id}")
        return book_id  # Возвращаем ID для других тестов
    except Exception as e:
        print_error(f"Ошибка добавления: {e}")
        return None

    # Тест 1.2: Пустое название
    try:
        service.add_book(title="   ", rating=5.0)
        print_error("Должна была возникнуть ошибка валидации названия")
    except ValueError as e:
        print_success(f"Валидация названия работает: {e}")

    # Тест 1.3: Некорректная оценка
    try:
        service.add_book(title="Тест", rating=15.0)
        print_error("Должна была возникнуть ошибка валидации оценки")
    except ValueError as e:
        print_success(f"Валидация оценки работает: {e}")

    # Тест 1.4: Некорректный год
    try:
        service.add_book(title="Тест", year=500)
        print_error("Должна была возникнуть ошибка валидации года")
    except ValueError as e:
        print_success(f"Валидация года работает: {e}")


def test_update_book(book_id):
    """Тест операции 2: Редактирование книги."""
    print_separator("Тест 2: Редактирование книги")
    service = BookService()

    if book_id is None:
        print_error("Нет ID книги для редактирования (предыдущий тест не прошёл)")
        return

    # Тест 2.1: Успешное редактирование
    try:
        success = service.update_book(
            item_id=book_id,
            title="Обновлённая книга",
            year=2021,
            rating=9.0,
            status_id=2,
            genre_ids=[1, 2],
            author_ids=[1]
        )
        print_success(f"Книга обновлена: {success}")
    except Exception as e:
        print_error(f"Ошибка редактирования: {e}")

    # Тест 2.2: Редактирование несуществующей книги
    try:
        service.update_book(item_id=9999, title="Тест")
        print_error("Должна была возникнуть ошибка отсутствия книги")
    except RuntimeError as e:
        print_success(f"Проверка существования работает: {e}")

    # Тест 2.3: Пустое название при редактировании
    try:
        service.update_book(item_id=book_id, title="")
        print_error("Должна была возникнуть ошибка валидации")
    except ValueError as e:
        print_success(f"Валидация при редактировании работает: {e}")


def test_delete_book(book_id):
    """Тест операции 3: Удаление книги."""
    print_separator("Тест 3: Удаление книги")
    service = BookService()

    if book_id is None:
        print_error("Нет ID книги для удаления")
        return

    # Тест 3.1: Успешное удаление
    try:
        success = service.delete_book(book_id)
        print_success(f"Книга удалена: {success}")
    except Exception as e:
        print_error(f"Ошибка удаления: {e}")

    # Тест 3.2: Удаление несуществующей книги
    try:
        service.delete_book(9999)
        print_error("Должна была возникнуть ошибка отсутствия книги")
    except RuntimeError as e:
        print_success(f"Проверка существования при удалении работает: {e}")


def test_search_and_filter():
    """Тест операции 4: Поиск и фильтрация."""
    print_separator("Тест 4: Поиск и фильтрация")
    service = BookService()

    # Тест 4.1: Поиск по названию
    try:
        results = service.search_and_filter(search_query="Властелин")
        print_success(f"Найдено книг по запросу 'Властелин': {len(results)}")
        for r in results:
            print(f"    - {r['title']}")
    except Exception as e:
        print_error(f"Ошибка поиска: {e}")

    # Тест 4.2: Фильтрация по статусу
    try:
        results = service.search_and_filter(status_id=1)
        print_success(f"Книг со статусом ID=1: {len(results)}")
    except Exception as e:
        print_error(f"Ошибка фильтрации: {e}")

    # Тест 4.3: Комбинированный поиск + фильтр + сортировка
    try:
        results = service.search_and_filter(
            search_query="Толкин",
            status_id=3,
            sort_by="rating",
            sort_order="desc"
        )
        print_success(f"Комбинированный запрос: найдено {len(results)} книг")
    except Exception as e:
        print_error(f"Ошибка комбинированного запроса: {e}")

    # Тест 4.4: Некорректная сортировка (защита от инъекций)
    try:
        service.search_and_filter(sort_by="id; DROP TABLE items")
        print_error("Должна была возникнуть ошибка валидации сортировки")
    except ValueError as e:
        print_success(f"Защита от SQL-инъекций работает: {e}")


def test_analytics():
    """Тест операции 5: Расчёт аналитики."""
    print_separator("Тест 5: Расчёт аналитики")
    service = AnalyticsService()

    try:
        analytics = service.get_analytics()
        print_success("Аналитика рассчитана:")
        print(f"    Всего книг: {analytics['total_books']}")
        print(f"    Средняя оценка: {analytics['average_rating']}")
        print(f"    Завершено: {analytics['completed_count']} ({analytics['completed_percent']}%)")
        print(f"    Распределение по статусам: {len(analytics['status_distribution'])} статусов")
        print(f"    Распределение по жанрам: {len(analytics['genre_distribution'])} жанров")
    except Exception as e:
        print_error(f"Ошибка расчёта аналитики: {e}")


def main():
    """Запуск всех тестов."""
    print("\n" + "="*70)
    print("  КОНСОЛЬНЫЕ ТЕСТЫ СЛОЯ БИЗНЕС-ЛОГИКИ (SERVICE LAYER)")
    print("="*70)

    # Инициализация БД
    print_separator("Инициализация базы данных")
    initialize_db()

    # Запуск тестов
    book_id = test_add_book()
    test_update_book(book_id)
    test_delete_book(book_id)
    test_search_and_filter()
    test_analytics()

    print_separator("ИТОГ")
    print("  Все тесты выполнены!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
