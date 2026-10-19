import sys
import os

# Добавляем папку src в путь, чтобы импорты работали
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import initialize_db
from dao.reference_dao import StatusDAO, GenreDAO, AuthorDAO
from dao.item_dao import ItemDAO
from dao.relation_dao import RelationDAO


def print_separator(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def main():
    # 1. Инициализация БД
    print_separator("1. ИНИЦИАЛИЗАЦИЯ БД")
    initialize_db()

    # Создаём DAO-объекты
    status_dao = StatusDAO()
    genre_dao = GenreDAO()
    author_dao = AuthorDAO()
    item_dao = ItemDAO()
    relation_dao = RelationDAO()

    # 2. Заполнение справочников
    print_separator("2. ДОБАВЛЕНИЕ СПРАВОЧНИКОВ")
    s1 = status_dao.insert("Запланировано")
    s2 = status_dao.insert("В процессе")
    s3 = status_dao.insert("Завершено")
    print(f"Статусы: id={s1}, {s2}, {s3}")

    g1 = genre_dao.insert("Фэнтези")
    g2 = genre_dao.insert("Фантастика")
    g3 = genre_dao.insert("Классика")
    print(f"Жанры: id={g1}, {g2}, {g3}")

    a1 = author_dao.insert("Дж. Р. Р. Толкин")
    a2 = author_dao.insert("Фрэнк Герберт")
    a3 = author_dao.insert("Фёдор Достоевский")
    print(f"Авторы: id={a1}, {a2}, {a3}")

    # 3. Добавление книг
    print_separator("3. ДОБАВЛЕНИЕ КНИГ")
    book1_id = item_dao.insert("Властелин колец: Братство кольца", 1954, 9.0, s3)
    book2_id = item_dao.insert("Дюна", 1965, 8.5, s2)
    book3_id = item_dao.insert("Преступление и наказание", 1866, 9.5, s1)
    print(f"Добавлены книги: id={book1_id}, {book2_id}, {book3_id}")

    # 4. Привязка жанров и авторов
    print_separator("4. СВЯЗИ M:N")
    relation_dao.add_genre(book1_id, g1)
    relation_dao.add_author(book1_id, a1)
    relation_dao.add_genre(book2_id, g2)
    relation_dao.add_author(book2_id, a2)
    relation_dao.add_genre(book3_id, g3)
    relation_dao.add_author(book3_id, a3)
    print("Жанры и авторы привязаны к книгам")

    # 5. Получение всех книг с деталями
    print_separator("5. СПИСОК ВСЕХ КНИГ С ДЕТАЛЯМИ")
    books = item_dao.get_all_with_details()
    for b in books:
        print(f"- {b['title']} ({b['year']}) | {b['status_name']} | "
              f"Оценка: {b['rating']} | Автор: {b['authors']} | Жанр: {b['genres']}")

    # 6. Поиск
    print_separator("6. ПОИСК ПО 'Толкин'")
    results = item_dao.search("Толкин")
    for r in results:
        print(f"- {r['title']} (статус: {r['status_name']})")

    # 7. Фильтрация по статусу
    print_separator(f"7. ФИЛЬТР: СТАТУС 'Завершено' (id={s3})")
    filtered = item_dao.filter_by_status(s3)
    for f in filtered:
        print(f"- {f['title']} | Оценка: {f['rating']}")

    # 8. Аналитика
    print_separator("8. АНАЛИТИКА")
    total = item_dao.get_total_count()
    avg_rating = item_dao.get_average_rating()
    print(f"Всего книг: {total}")
    print(f"Средняя оценка: {avg_rating}")

    print("\nРаспределение по статусам:")
    dist = item_dao.get_distribution_by_status()
    for d in dist:
        print(f"  - {d['status_name']}: {d['book_count']} книг")

    # 9. Обновление книги
    print_separator("9. ОБНОВЛЕНИЕ КНИГИ")
    item_dao.update(book2_id, "Дюна", 1965, 9.0, s3)
    print(f"Книга id={book2_id} обновлена: рейтинг=9.0, статус=Завершено")

    # 10. Удаление книги
    print_separator("10. УДАЛЕНИЕ КНИГИ")
    deleted = item_dao.delete(book3_id)
    print(f"Книга id={book3_id} удалена: {deleted}")

    print_separator("ИТОГ")
    print("Все тесты выполнены успешно!")


if __name__ == "__main__":
    main()
