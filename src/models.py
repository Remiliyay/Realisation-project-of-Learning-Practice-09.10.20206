class Status:
    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name

    def __repr__(self):
        return f"Status(id={self.id}, name='{self.name}')"


class Genre:
    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name

    def __repr__(self):
        return f"Genre(id={self.id}, name='{self.name}')"


class Author:
    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name

    def __repr__(self):
        return f"Author(id={self.id}, name='{self.name}')"


class Item:
    def __init__(self, id=None, title=None, year=None, rating=None,
                 status_id=None, notes=None):
        self.id = id
        self.title = title
        self.year = year
        self.rating = rating
        self.status_id = status_id
        self.notes = notes

    def __repr__(self):
        return f"Item(id={self.id}, title='{self.title}', rating={self.rating})"
