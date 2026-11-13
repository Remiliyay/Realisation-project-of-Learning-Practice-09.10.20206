"""
Окно аналитики "Коллекция в цифрах".

Использует только AnalyticsService (никакого SQL напрямую).
"""

import tkinter as tk

from services.analytics_service import AnalyticsService
from ui.theme import (ACCENT, BG_CARD, BG_MAIN,
                      TEXT_PRIMARY, TEXT_SECONDARY)

## Символ текстовой полосы для диаграмм
BAR_CHAR = "█"


class AnalyticsWindow(tk.Toplevel):
    """Окно со статистикой коллекции."""

    def __init__(self, parent):
        super().__init__(parent)
        self.service = AnalyticsService()

        self.title("Коллекция в цифрах")
        self.configure(bg=BG_MAIN)
        self.geometry("640x560")
        self.minsize(520, 420)
        self.transient(parent)

        try:
            data = self.service.get_analytics()
        except (ValueError, RuntimeError) as e:
            self._show_message(f"Не удалось получить статистику: {e}")
            return

        if data["total_books"] == 0:
            self._show_message("Добавьте первую книгу, чтобы увидеть статистику.")
            return

        self._build_ui(data)

    # ===== Вспомогательная отрисовка =====

    def _show_message(self, text):
        frame = tk.Frame(self, bg=BG_MAIN)
        frame.pack(expand=True)
        tk.Label(frame, text=text, bg=BG_MAIN, fg=TEXT_SECONDARY,
                 font=("Segoe UI", 12)).pack(padx=30, pady=30)

    def _card(self, parent, title, value):
        card = tk.Frame(parent, bg=BG_CARD, highlightthickness=1,
                        highlightbackground="#D5D9D8")
        card.pack(side="left", fill="both", expand=True, padx=6, pady=6)
        tk.Label(card, text=value, bg=BG_CARD, fg=ACCENT,
                 font=("Segoe UI", 20, "bold")).pack(pady=(16, 2))
        tk.Label(card, text=title, bg=BG_CARD, fg=TEXT_SECONDARY,
                 font=("Segoe UI", 10)).pack(pady=(0, 16))

    def _section(self, parent, title):
        tk.Label(parent, text=title, bg=BG_MAIN, fg=TEXT_PRIMARY,
                 font=("Segoe UI", 12, "bold"), anchor="w").pack(
            fill="x", padx=18, pady=(14, 4))

    def _dist_row(self, parent, name, count, percent):
        row = tk.Frame(parent, bg=BG_MAIN)
        row.pack(fill="x", padx=18, pady=2)
        tk.Label(row, text=name, width=16, anchor="w", bg=BG_MAIN,
                 fg=TEXT_PRIMARY, font=("Segoe UI", 10)).pack(side="left")
        bar_len = max(0, round(percent / 5.0))
        tk.Label(row, text=BAR_CHAR * bar_len, bg=BG_MAIN, fg=ACCENT,
                 font=("Segoe UI", 10)).pack(side="left", padx=(4, 6))
        tk.Label(row, text=f"{count} ({percent}%)", bg=BG_MAIN,
                 fg=TEXT_SECONDARY, font=("Segoe UI", 10)).pack(side="left")

    # ===== Основной интерфейс =====

    def _build_ui(self, data):
        total = data["total_books"]

        # --- Три карточки ---
        cards = tk.Frame(self, bg=BG_MAIN)
        cards.pack(fill="x", padx=12, pady=(12, 4))
        self._card(cards, "Всего элементов", str(total))
        self._card(cards, "Средняя оценка /10", f"{data['average_rating']}")
        self._card(cards, "Завершено %", f"{data['completed_percent']}%")

        # --- Распределение по статусам ---
        self._section(self, "Распределение по статусам")
        for item in data["status_distribution"]:
            count = item["book_count"]
            percent = round(count / total * 100, 1) if total else 0.0
            self._dist_row(self, item["status_name"] or "Без статуса",
                           count, percent)

        # --- Топ-5 жанров ---
        self._section(self, "Топ-5 жанров")
        top_genres = [g for g in data["genre_distribution"]
                      if g["book_count"] > 0][:5]
        if not top_genres:
            tk.Label(self, text="Жанры пока не указаны", bg=BG_MAIN,
                     fg=TEXT_SECONDARY, font=("Segoe UI", 10)).pack(
                anchor="w", padx=18)
        for item in top_genres:
            count = item["book_count"]
            percent = round(count / total * 100, 1) if total else 0.0
            self._dist_row(self, item["genre_name"], count, percent)
