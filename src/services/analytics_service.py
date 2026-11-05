"""
Сервис для расчёта аналитики (бизнес-логика).
Операция: расчёт статистики коллекции.
"""

from dao.item_dao import ItemDAO


class AnalyticsService:
    """Сервис для расчёта статистики коллекции."""

    def __init__(self):
        self.item_dao = ItemDAO()

    def get_analytics(self):
        """
        Операция 5: Расчёт аналитики для дашборда.
        
        Результат:
            dict — словарь с метриками:
                - total_books: int (всего книг)
                - average_rating: float (средняя оценка)
                - completed_count: int (количество завершённых)
                - completed_percent: float (процент завершённых)
                - status_distribution: list[dict] (распределение по статусам)
                - genre_distribution: list[dict] (распределение по жанрам)
        """
        # Получение общего количества книг
        total = self.item_dao.get_total_count()

        # Обработка пустой коллекции
        if total == 0:
            return {
                "total_books": 0,
                "average_rating": 0.0,
                "completed_count": 0,
                "completed_percent": 0.0,
                "status_distribution": [],
                "genre_distribution": []
            }

        # Расчёт метрик
        avg_rating = self.item_dao.get_average_rating()
        status_dist = self.item_dao.get_distribution_by_status()
        genre_dist = self.item_dao.get_distribution_by_genre()

        # Поиск количества завершённых книг
        completed_count = 0
        for item in status_dist:
            if item["status_name"] == "Завершено":
                completed_count = item["book_count"]
                break

        # Расчёт процента завершённых
        completed_percent = round((completed_count / total) * 100, 1)

        return {
            "total_books": total,
            "average_rating": avg_rating,
            "completed_count": completed_count,
            "completed_percent": completed_percent,
            "status_distribution": status_dist,
            "genre_distribution": genre_dist
        }
