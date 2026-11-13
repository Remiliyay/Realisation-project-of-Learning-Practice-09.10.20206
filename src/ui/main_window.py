"""
Главный экран приложения "Моя Полка".

Взаимодействует только со слоями Service (BookService, AnalyticsService) —
SQL напрямую здесь не используется.
"""

import csv
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from services.book_service import BookService
from services.analytics_service import AnalyticsService
from ui.book_dialog import BookDialog
from ui.analytics_window import AnalyticsWindow
from ui.theme import (ACCENT, ACCENT_TEXT, BG_CARD, BG_MAIN,
                      TEXT_PRIMARY, TEXT_SECONDARY)

## Элемент фильтра "все статусы"
ALL_STATUSES = "Все статусы"


class MainWindow(tk.Frame):
    """Главное окно со списком книг, поиском, фильтрами и экспортом."""

    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.pack(fill="both", expand=True)
        self.configure(bg=BG_MAIN)

        # Стиль ttk применяем до создания виджетов Combobox/Treeview
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Treeview", background=BG_CARD, fieldbackground=BG_CARD,
                        foreground=TEXT_PRIMARY, rowheight=26, borderwidth=0)
        style.configure("Treeview.Heading", background="#EDEFEF",
                        foreground=TEXT_PRIMARY, font=("Segoe UI", 10, "bold"))

        self.book_service = BookService()
        self.analytics_service = AnalyticsService()

        # Справочники: name -> id
        self.status_by_name = {}
        # Текущая сортировка по клику на заголовки
        self.sort_by = None          # "rating" | "year" | None
        self.sort_order = "desc"
        # Последняя выбранная строка (для контекстного меню)
        self._menu_item_id = None

        self._build_ui()
        self.refresh()

    # ===== Построение интерфейса =====

    def _build_ui(self):
        # --- Шапка: заголовок + кнопки ---
        header = tk.Frame(self, bg=BG_MAIN)
        header.pack(fill="x", padx=16, pady=(14, 6))

        tk.Label(header, text="Моя коллекция", bg=BG_MAIN, fg=TEXT_PRIMARY,
                 font=("Segoe UI", 18, "bold")).pack(side="left")

        add_btn = tk.Button(header, text="+ Добавить элемент", command=self.on_add,
                            bg=ACCENT, fg=ACCENT_TEXT, activebackground="#25665C",
                            activeforeground=ACCENT_TEXT, relief="flat",
                            font=("Segoe UI", 10, "bold"), padx=12, pady=2)
        add_btn.pack(side="right")

        export_btn = tk.Button(header, text="Экспорт", command=self.on_export,
                               bg=BG_CARD, fg=TEXT_PRIMARY,
                               activebackground="#E5E7EB", padx=12, pady=2)
        export_btn.pack(side="right", padx=(0, 8))

        analytics_btn = tk.Button(header, text="Аналитика", command=self.on_analytics,
                                  bg=BG_CARD, fg=TEXT_PRIMARY,
                                  activebackground="#E5E7EB", padx=12, pady=2)
        analytics_btn.pack(side="right", padx=(0, 8))

        # --- Строка статистики ---
        self.stats_label = tk.Label(self, text="", bg=BG_MAIN, fg=TEXT_SECONDARY,
                                    font=("Segoe UI", 10), anchor="w")
        self.stats_label.pack(fill="x", padx=18)

        # --- Панель поиска и фильтра ---
        controls = tk.Frame(self, bg=BG_MAIN)
        controls.pack(fill="x", padx=16, pady=(10, 6))

        self.search_var = tk.StringVar()
        search_entry = tk.Entry(controls, textvariable=self.search_var, width=40,
                                bg=BG_CARD, fg=TEXT_PRIMARY,
                                insertbackground=TEXT_PRIMARY,
                                highlightthickness=1,
                                highlightbackground="#D5D9D8")
        search_entry.pack(side="left")
        # Плейсхолдер
        search_entry.bind("<FocusIn>", self._on_search_focus_in)
        search_entry.bind("<FocusOut>", self._on_search_focus_out)
        self._activate_placeholder(search_entry)

        # Строка "Показано X из Y" (создаём до первого refresh)
        self.count_label = tk.Label(self, text="", bg=BG_MAIN, fg=TEXT_SECONDARY,
                                    font=("Segoe UI", 9), anchor="w")

        self.filter_var = tk.StringVar(value=ALL_STATUSES)
        self.filter_combo = ttk.Combobox(controls, textvariable=self.filter_var,
                                         state="readonly", width=18)
        self.filter_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh())
        self.filter_combo.pack(side="left", padx=(10, 0))

        # --- Таблица ---
        table_frame = tk.Frame(self, bg=BG_MAIN)
        table_frame.pack(fill="both", expand=True, padx=16)

        columns = ("title", "author", "genre", "status", "rating", "year")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                                 selectmode="browse")
        headings = {
            "title": ("Название", 320, "w"),
            "author": ("Автор", 180, "w"),
            "genre": ("Жанр", 160, "w"),
            "status": ("Статус", 120, "w"),
            "rating": ("Оценка", 80, "center"),
            "year": ("Год", 80, "center"),
        }
        for col, (text, width, anchor) in headings.items():
            self.tree.heading(col, text=text,
                              command=lambda c=col: self.on_heading_click(c))
            self.tree.column(col, width=width, anchor=anchor, stretch=(col == "title"))

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # Цветовые метки для статусов
        self.tree.tag_configure("done", foreground="#2D7A6E")
        self.tree.tag_configure("progress", foreground="#B7791F")
        self.tree.tag_configure("planned", foreground="#6B7280")

        # Контекстное меню по правому клику
        self.tree.bind("<Button-3>", self.on_right_click)
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="Редактировать", command=self.on_edit_selected)
        self.context_menu.add_command(label="Удалить", command=self.on_delete_selected)

        # Двойной клик — быстрое редактирование
        self.tree.bind("<Double-1>", lambda e: self.on_edit_selected())

        # --- Размещение нижней строки ---
        self.count_label.pack(fill="x", padx=18, pady=(6, 10))

        # Мгновенная фильтрация при вводе (подключаем после построения UI)
        self.search_var.trace_add("write", lambda *args: self.refresh())

    # ===== Плейсхолдер поиска =====

    PLACEHOLDER = "Поиск по названию или автору..."

    def _activate_placeholder(self, entry):
        """Включает режим плейсхолдера в поле поиска."""
        self._placeholder_active = True
        entry.configure(fg=TEXT_SECONDARY)
        entry.delete(0, "end")
        entry.insert(0, self.PLACEHOLDER)

    def _on_search_focus_in(self, event):
        entry = event.widget
        if getattr(self, "_placeholder_active", False):
            entry.delete(0, "end")
            entry.configure(fg=TEXT_PRIMARY)
            self._placeholder_active = False

    def _on_search_focus_out(self, event):
        entry = event.widget
        if not entry.get().strip():
            self._activate_placeholder(entry)

    # ===== Данные и обновление =====

    def _get_search_query(self):
        if getattr(self, "_placeholder_active", False):
            return None
        text = self.search_var.get().strip()
        return text if text else None

    def refresh(self):
        """Перезагружает таблицу, статистику и список статусов."""
        # Справочник статусов для фильтра
        try:
            statuses = list(self.book_service.get_statuses())
        except (ValueError, RuntimeError) as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить статусы: {e}")
            statuses = []
        self.status_by_name = {s["name"]: s["id"] for s in statuses}
        values = [ALL_STATUSES] + [s["name"] for s in statuses]
        current = self.filter_var.get()
        self.filter_combo["values"] = values
        self.filter_var.set(current if current in values else ALL_STATUSES)

        # Параметры запроса
        query = self._get_search_query()
        status_id = None
        if self.filter_var.get() != ALL_STATUSES:
            status_id = self.status_by_name.get(self.filter_var.get())

        # Загрузка данных
        try:
            if self.sort_by is not None:
                books = self.book_service.search_and_filter(
                    search_query=query, status_id=status_id,
                    sort_by=self.sort_by, sort_order=self.sort_order)
            else:
                books = self.book_service.search_and_filter(
                    search_query=query, status_id=status_id)
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
            books = []
        except RuntimeError as e:
            messagebox.showerror("Ошибка",
                                 "Не удалось загрузить коллекцию. "
                                 "Проверьте файл базы данных.")
            books = []

        # Обновление таблицы
        selected = self.tree.selection()
        selected_iid = selected[0] if selected else None
        self.tree.delete(*self.tree.get_children())
        for b in books:
            keys = b.keys()
            tags = self._tags_for_status(b["status_name"])
            self.tree.insert("", "end", iid=str(b["id"]), values=(
                b["title"],
                b["authors"] if "authors" in keys else "",
                b["genres"] if "genres" in keys else "",
                b["status_name"] or "",
                self._format_rating(b["rating"]),
                b["year"] if b["year"] is not None else "",
            ), tags=tags)
        if selected_iid and self.tree.exists(selected_iid):
            self.tree.selection_set(selected_iid)

        # Подсказка, если ничего не найдено
        if not books and (query or status_id is not None):
            self.count_label.config(
                text="Ничего не найдено. Попробуйте изменить запрос.")
        else:
            total_shown = len(books)
            try:
                total_all = self.analytics_service.get_analytics()["total_books"]
            except (ValueError, RuntimeError):
                total_all = total_shown
            self.count_label.config(
                text=f"Показано {total_shown} из {total_all} элементов")

        # Строка статистики в шапке
        try:
            data = self.analytics_service.get_analytics()
            self.stats_label.config(text=(
                f"{data['total_books']} элементов   |   "
                f"{data['average_rating']} средняя оценка   |   "
                f"{data['completed_count']} из {data['total_books']} завершено"))
        except (ValueError, RuntimeError) as e:
            self.stats_label.config(text=f"Не удалось загрузить статистику: {e}")

        # Стрелки в заголовках сортируемых колонок
        self.tree.heading("rating", text=self._heading_text("rating", "Оценка"))
        self.tree.heading("year", text=self._heading_text("year", "Год"))

    @staticmethod
    def _format_rating(rating):
        if rating is None:
            return ""
        if float(rating) == int(float(rating)):
            return f"☆ {int(float(rating))}/10"
        return f"☆ {rating}/10"

    @staticmethod
    def _tags_for_status(status_name):
        if status_name == "Завершено":
            return ("done",)
        if status_name == "В процессе":
            return ("progress",)
        return ("planned",)

    def _heading_text(self, column, base):
        if self.sort_by == column:
            arrow = "▼" if self.sort_order == "desc" else "▲"
            return f"{base} {arrow}"
        return base

    # ===== Действия =====

    def on_heading_click(self, column):
        """Сортировка по клику на заголовок (только Оценка и Год)."""
        if column not in ("rating", "year"):
            return
        if self.sort_by == column:
            self.sort_order = "asc" if self.sort_order == "desc" else "desc"
        else:
            self.sort_by = column
            self.sort_order = "desc"
        self.refresh()

    def on_add(self):
        BookDialog(self.master, item_id=None, on_saved=self.refresh)

    def on_analytics(self):
        try:
            AnalyticsWindow(self.master)
        except (ValueError, RuntimeError) as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть аналитику: {e}")

    def on_right_click(self, event):
        iid = self.tree.identify_row(event.y)
        if not iid:
            return
        self.tree.selection_set(iid)
        self._menu_item_id = int(iid)
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def _selected_item_id(self):
        selected = self.tree.selection()
        if not selected:
            return None
        return int(selected[0])

    def on_edit_selected(self):
        item_id = self._selected_item_id() or self._menu_item_id
        if item_id is None:
            return
        BookDialog(self.master, item_id=item_id, on_saved=self.refresh)

    def on_delete_selected(self):
        item_id = self._selected_item_id() or self._menu_item_id
        if item_id is None:
            return
        title = self.tree.item(str(item_id), "values")[0]
        confirm = messagebox.askyesno(
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить книгу «{title}»? "
            "Это действие нельзя отменить.")
        if not confirm:
            return
        try:
            self.book_service.delete_book(item_id)
        except (ValueError, RuntimeError) as e:
            messagebox.showerror("Ошибка", str(e))
            return
        self.refresh()

    # ===== Экспорт =====

    def _collect_rows(self):
        """Формирует список словарей для экспорта через сервисный слой."""
        try:
            books = self.book_service.search_and_filter()
        except (ValueError, RuntimeError) as e:
            raise RuntimeError(f"Не удалось получить данные для экспорта: {e}")
        rows = []
        for b in books:
            keys = b.keys()
            rows.append({
                "Название": b["title"],
                "Автор": b["authors"] if "authors" in keys else "",
                "Жанр": b["genres"] if "genres" in keys else "",
                "Статус": b["status_name"] or "",
                "Оценка": b["rating"] if b["rating"] is not None else "",
                "Год": b["year"] if b["year"] is not None else "",
            })
        return rows

    def on_export(self):
        try:
            rows = self._collect_rows()
        except RuntimeError as e:
            messagebox.showerror("Ошибка", str(e))
            return

        if not rows:
            messagebox.showwarning("Пустая коллекция",
                                   "Коллекция пуста. Нечего экспортировать.")
            return

        path = filedialog.asksaveasfilename(
            title="Экспорт коллекции",
            defaultextension=".csv",
            filetypes=[("CSV файлы", "*.csv"), ("JSON файлы", "*.json")])
        if not path:
            return

        try:
            if path.lower().endswith(".json"):
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(rows, f, ensure_ascii=False, indent=2)
            else:
                with open(path, "w", encoding="utf-8", newline="") as f:
                    writer = csv.DictWriter(
                        f, fieldnames=["Название", "Автор", "Жанр",
                                       "Статус", "Оценка", "Год"])
                    writer.writeheader()
                    writer.writerows(rows)
        except OSError as e:
            messagebox.showerror("Ошибка", f"Не удалось записать файл: {e}")
            return

        messagebox.showinfo("Экспорт завершён",
                            f"Коллекция экспортирована в файл:\n{path}")
