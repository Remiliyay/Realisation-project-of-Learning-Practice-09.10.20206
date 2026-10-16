# Часть 2. Проектирование DAO-слоя и SQL-запросы

## 2.1. Описание DAO-классов и методов (CRUD)

### Класс `ItemDAO` (Работа с таблицей `items` - Книги)

**1. Метод: `getAll()`**
* **Входные параметры:** нет
* **Возвращаемое значение:** `List<Item>` (список объектов книг)
* **SQL-запрос:** `SELECT id, title, year, rating, status_id, notes FROM items`

**2. Метод: `getById(id)`**
* **Входные параметры:** `int id`
* **Возвращаемое значение:** `Item` (объект книги) или `null`
* **SQL-запрос:** `SELECT id, title, year, rating, status_id, notes FROM items WHERE id = ?`

**3. Метод: `insert(item)`**
* **Входные параметры:** `Item item` (объект с заполненными полями)
* **Возвращаемое значение:** `long` (сгенерированный ID новой записи)
* **SQL-запрос:** `INSERT INTO items (title, year, rating, status_id, notes) VALUES (?, ?, ?, ?, ?)`

**4. Метод: `update(item)`**
* **Входные параметры:** `Item item` (объект с обновлёнными данными и существующим ID)
* **Возвращаемое значение:** `boolean` (true, если обновлена 1 строка)
* **SQL-запрос:** `UPDATE items SET title = ?, year = ?, rating = ?, status_id = ?, notes = ? WHERE id = ?`

**5. Метод: `delete(id)`**
* **Входные параметры:** `int id`
* **Возвращаемое значение:** `boolean` (true, если удалено)
* **SQL-запрос:** `DELETE FROM items WHERE id = ?`

---

### Класс `ReferenceDAO` (Работа со справочниками: `statuses`, `genres`, `authors`)
*(Для краткости приведён обобщённый пример для таблицы `statuses`, для `genres` и `authors` логика идентична)*

**1. Метод: `getAllStatuses()`**
* **Входные параметры:** нет
* **Возвращаемое значение:** `List<Status>`
* **SQL-запрос:** `SELECT id, name FROM statuses ORDER BY name`

**2. Метод: `insertStatus(name)`**
* **Входные параметры:** `String name`
* **Возвращаемое значение:** `long` (новый ID)
* **SQL-запрос:** `INSERT INTO statuses (name) VALUES (?)`

---

### Класс `ItemRelationDAO` (Работа со связями M:N)
*(Стандартный CRUD здесь не применим, используются специфичные методы)*

**1. Метод: `addGenreToItem(itemId, genreId)`**
* **Входные параметры:** `int itemId`, `int genreId`
* **Возвращаемое значение:** `void`
* **SQL-запрос:** `INSERT INTO item_genres (item_id, genre_id) VALUES (?, ?)`

**2. Метод: `deleteGenresByItem(itemId)`** *(Нужен для обновления жанров книги)*
* **Входные параметры:** `int itemId`
* **Возвращаемое значение:** `void`
* **SQL-запрос:** `DELETE FROM item_genres WHERE item_id = ?`

---

## 2.2. SQL-запросы для бизнес-логики

Эти запросы решают конкретные задачи пользователя из брифа, используя `JOIN`, `GROUP BY` и агрегатные функции.

### Операция 1: Получение полного списка книг с именами авторов и жанров
* **Описание:** Выводит таблицу книг, где вместо ID статусов, авторов и жанров подставляются их читаемые названия. Используется `GROUP_CONCAT` для склеивания нескольких авторов/жанров в одну строку.
* **Входные параметры:** нет
* **Возвращаемое значение:** `List<BookViewDTO>` (специальный объект для отображения)
* **SQL-запрос:**
  ```sql
  SELECT 
      i.id, 
      i.title, 
      i.year, 
      i.rating, 
      s.name AS status_name,
      GROUP_CONCAT(DISTINCT a.name, ', ') AS authors,
      GROUP_CONCAT(DISTINCT g.name, ', ') AS genres
  FROM items i
  LEFT JOIN statuses s ON i.status_id = s.id
  LEFT JOIN item_authors ia ON i.id = ia.item_id
  LEFT JOIN authors a ON ia.author_id = a.id
  LEFT JOIN item_genres ig ON i.id = ig.item_id
  LEFT JOIN genres g ON ig.genre_id = g.id
  GROUP BY i.id
  ORDER BY i.year DESC;
