"""
Модальное окно добавления / редактирования книги.

Использует только BookService (никакого SQL напрямую).
"""

import tkinter as tk
from tkinter import ttk, messagebox

from services.book_service import BookService
from ui.theme import (ACCENT, ACCENT_TEXT, BG_CARD, BG_MAIN,
                      TEXT_PRIMARY, TEXT_SECONDARY, TEXT_ERROR)


class BookDialog(tk.Toplevel):
    """Модальное окно 'Добавить элемент' / 'Редактировать элемент'."""

    def __init__(self, parent, item_id=None, on_saved=None):
        super().__init__(parent)
        self.service = BookService()
        self.item_id = item_id
        self.on_saved = on_saved

        self.title("Редактировать элемент" if item_id else "Добавить элемент")
        self.configure(bg=BG_MAIN)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # Справочники
        self.statuses = list(self.service.get_statuses())
        self.genres = list(self.service.get_genres())
        self.authors = list(self.service.get_authors())

        # Состояние формы
        self.rating_var = tk.IntVar(value=0)
        self.rating_buttons = []

        self._build_ui()
        if item_id is not None:
            self._load_book()

        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.bind("<Escape>", lambda e: self._on_cancel())

        # Центрируем относительно родителя
        self.update_idletasks()
        try:
            x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
            y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 3
            self.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        except tk.TclError:
            pass

    # ===== Построение интерфейса =====

    def _build_ui(self):
        pad = {"padx": 16, "pady": 6}
        body = tk.Frame(self, bg=BG_MAIN)
        body.pack(fill="both", expand=True, padx=8, pady=8)

        # --- Название ---
        tk.Label(body, text="Название *", bg=BG_MAIN, fg=TEXT_PRIMARY,
                 font=("Segoe UI", 10, "bold"), anchor="w").grid(
            row=0, column=0, sticky="w", **pad)
        self.title_entry = tk.Entry(body, width=52, bg=BG_CARD, fg=TEXT_PRIMARY,
                                    insertbackground=TEXT_PRIMARY,
                                    highlightthickness=1,
                                    highlightbackground="#D5D9D8")
        self.title_entry.grid(row=1, column=0, sticky="we", **pad)

        # Сообщение об ошибке валидации (под полем "Название")
        self.error_label = tk.Label(body, text="", bg=BG_MAIN, fg=TEXT_ERROR,
                                    font=("Segoe UI", 9), anchor="w", justify="left")
        self.error_label.grid(row=2, column=0, sticky="w", padx=16)

        # --- Год издания ---
        tk.Label(body, text="Год издания", bg=BG_MAIN, fg=TEXT_PRIMARY,
                 font=("Segoe UI", 10, "bold"), anchor="w").grid(
            row=3, column=0, sticky="w", **pad)
        self.year_entry = tk.Entry(body, width=52, bg=BG_CARD, fg=TEXT_PRIMARY,
                                   insertbackground=TEXT_PRIMARY,
                                   highlightthickness=1,
                                   highlightbackground="#D5D9D8")
        self.year_entry.grid(row=4, column=0, sticky="we", **pad)

        # --- Статус ---
        tk.Label(body, text="Статус", bg=BG_MAIN, fg=TEXT_PRIMARY,
                 font=("Segoe UI", 10, "bold"), anchor="w").grid(
            row=5, column=0, sticky="w", **pad)
        self.status_var = tk.StringVar()
        status_names = [s["name"] for s in self.statuses]
        self.status_combo = ttk.Combobox(body, textvariable=self.status_var,
                                         values=status_names, state="readonly",
                                         width=50)
        self.status_combo.grid(row=6, column=0, sticky="we", **pad)
        if status_names:
            self.status_combo.current(0)

        # --- Жанры и Авторы (два Listbox рядом) ---
        lists_frame = tk.Frame(body, bg=BG_MAIN)
        lists_frame.grid(row=7, column=0, sticky="we", **pad)

        tk.Label(lists_frame, text="Жанры", bg=BG_MAIN, fg=TEXT_PRIMARY,
                 font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", padx=(0, 8))
        tk.Label(lists_frame, text="Авторы", bg=BG_MAIN, fg=TEXT_PRIMARY,
                 font=("Segoe UI", 10, "bold")).grid(row=0, column=1, sticky="w")

        self.genre_listbox = tk.Listbox(lists_frame, selectmode="extended",
                                        height=5, width=24, bg=BG_CARD,
                                        fg=TEXT_PRIMARY, activestyle="none",
                                        highlightthickness=1,
                                        highlightbackground="#D5D9D8",
                                        exportselection=False)
        self.genre_listbox.grid(row=1, column=0, sticky="we", padx=(0, 8))
        for g in self.genres:
            self.genre_listbox.insert("end", g["name"])

        self.author_listbox = tk.Listbox(lists_frame, selectmode="extended",
                                         height=5, width=24, bg=BG_CARD,
                                         fg=TEXT_PRIMARY, activestyle="none",
                                         highlightthickness=1,
                                         highlightbackground="#D5D9D8",
                                         exportselection=False)
        self.author_listbox.grid(row=1, column=1, sticky="we")
        for a in self.authors:
            self.author_listbox.insert("end", a["name"])

        # --- Оценка: ряд кнопок 1-10 ---
        tk.Label(body, text="Оценка", bg=BG_MAIN, fg=TEXT_PRIMARY,
                 font=("Segoe UI", 10, "bold"), anchor="w").grid(
            row=8, column=0, sticky="w", **pad)
        rating_frame = tk.Frame(body, bg=BG_MAIN)
        rating_frame.grid(row=9, column=0, sticky="w", **pad)
        for value in range(1, 11):
            btn = tk.Button(rating_frame, text=str(value), width=3,
                            command=lambda v=value: self._set_rating(v))
            btn.pack(side="left", padx=2)
            self.rating_buttons.append(btn)
        self.rating_caption = tk.Label(rating_frame, text="", bg=BG_MAIN,
                                       fg=TEXT_SECONDARY, font=("Segoe UI", 9))
        self.rating_caption.pack(side="left", padx=8)
        self._refresh_rating_buttons()

        # --- Сноска ---
        tk.Label(body, text="* Обязательное поле. Остальное можно изменить позже.",
                 bg=BG_MAIN, fg=TEXT_SECONDARY, font=("Segoe UI", 9),
                 anchor="w").grid(row=10, column=0, sticky="w", **pad)

        # --- Кнопки ---
        btns = tk.Frame(body, bg=BG_MAIN)
        btns.grid(row=11, column=0, sticky="e", **pad)
        tk.Button(btns, text="Отмена", width=12, command=self._on_cancel,
                  bg=BG_CARD, fg=TEXT_PRIMARY, activebackground="#E5E7EB").pack(
            side="left", padx=(0, 8))
        tk.Button(btns, text="Сохранить", width=12, command=self._on_save,
                  bg=ACCENT, fg=ACCENT_TEXT, activebackground="#25665C",
                  activeforeground=ACCENT_TEXT).pack(side="left")

        body.grid_columnconfigure(0, weight=1)
        lists_frame.grid_columnconfigure(0, weight=1)
        lists_frame.grid_columnconfigure(1, weight=1)

    # ===== Логика оценки =====

    def _set_rating(self, value):
        # Повторный клик по выбранной оценке сбрасывает её
        if self.rating_var.get() == value:
            self.rating_var.set(0)
        else:
            self.rating_var.set(value)
        self._refresh_rating_buttons()

    def _refresh_rating_buttons(self):
        selected = self.rating_var.get()
        for idx, btn in enumerate(self.rating_buttons, start=1):
            if idx == selected:
                btn.configure(bg=ACCENT, fg=ACCENT_TEXT,
                              activebackground="#25665C", activeforeground=ACCENT_TEXT)
            else:
                btn.configure(bg=BG_CARD, fg=TEXT_PRIMARY,
                              activebackground="#E5E7EB", activeforeground=TEXT_PRIMARY)
        self.rating_caption.config(
            text=f"{selected} из 10" if selected else "Не указана")

    # ===== Предзаполнение (режим редактирования) =====

    def _load_book(self):
        try:
            book, genre_ids, author_ids = self.service.get_book_for_edit(self.item_id)
        except RuntimeError as e:
            messagebox.showerror("Ошибка", str(e), parent=self)
            self.destroy()
            return

        self.title_entry.insert(0, book["title"] or "")
        if book["year"] is not None:
            self.year_entry.insert(0, str(book["year"]))

        # Статус
        for i, s in enumerate(self.statuses):
            if s["id"] == book["status_id"]:
                self.status_combo.current(i)
                break

        # Жанры
        for i, g in enumerate(self.genres):
            if g["id"] in genre_ids:
                self.genre_listbox.selection_set(i)

        # Авторы
        for i, a in enumerate(self.authors):
            if a["id"] in author_ids:
                self.author_listbox.selection_set(i)

        # Оценка
        if book["rating"] is not None:
            self.rating_var.set(int(book["rating"]))
            self._refresh_rating_buttons()

    # ===== Сохранение / отмена =====

    def _get_selected_ids(self, listbox, reference):
        return [reference[i]["id"] for i in listbox.curselection()]

    def _on_save(self):
        self.error_label.config(text="")

        title = self.title_entry.get().strip()

        # Год издания
        year_text = self.year_entry.get().strip()
        year = None
        if year_text:
            try:
                year = int(year_text)
            except ValueError:
                self.error_label.config(
                    text="Год издания должен быть целым числом")
                return

        # Статус
        status_id = None
        status_name = self.status_var.get()
        for s in self.statuses:
            if s["name"] == status_name:
                status_id = s["id"]
                break

        # Оценка
        rating = self.rating_var.get() or None

        genre_ids = self._get_selected_ids(self.genre_listbox, self.genres)
        author_ids = self._get_selected_ids(self.author_listbox, self.authors)

        try:
            if self.item_id is None:
                self.service.add_book(title=title, year=year, rating=rating,
                                      status_id=status_id,
                                      genre_ids=genre_ids, author_ids=author_ids)
            else:
                self.service.update_book(item_id=self.item_id, title=title,
                                         year=year, rating=rating,
                                         status_id=status_id,
                                         genre_ids=genre_ids,
                                         author_ids=author_ids)
        except ValueError as e:
            # Ошибка валидации — показываем красным под полем "Название",
            # окно НЕ закрываем
            self.error_label.config(text=str(e))
            return
        except RuntimeError as e:
            messagebox.showerror("Ошибка", str(e), parent=self)
            return

        if self.on_saved:
            self.on_saved()
        self.destroy()

    def _on_cancel(self):
        self.destroy()
