
from abc import ABC, abstractmethod
from datetime import date

class Entity(ABC):

    def __init__(self, entity_id: str):
        self._id = str(entity_id).strip()
        if not self._id:
            raise ValueError("Идентификатор не может быть пустым")

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        value = str(value).strip()
        if not value:
            raise ValueError("Идентификатор не может быть пустым")
        self._id = value

    @abstractmethod
    def to_dict(self) -> dict:
        pass

    @abstractmethod
    def display_name(self) -> str:
        pass

class Book(Entity):

    VALID_STATUSES = ("В библиотеке", "Выдана")

    def __init__(self, entity_id: str, title: str, author: str, year: int,
                 genre: str = "Не указан", isbn: str = "", status: str = "В библиотеке",
                 borrower: str = ""):
        super().__init__(entity_id)
        self.title = title
        self.author = author
        self.year = year
        self.genre = genre
        self.isbn = isbn
        self.status = status
        self.borrower = borrower

    @property
    def title(self) -> str:
        return self._title
    @title.setter
    def title(self, value: str) -> None:
        value = str(value).strip()
        if not value:
            raise ValueError("Название книги обязательно")
        self._title = value

    @property
    def author(self) -> str:
        return self._author
    @author.setter
    def author(self, value: str) -> None:
        value = str(value).strip()
        if not value:
            raise ValueError("Автор обязателен")
        self._author = value

    @property
    def year(self) -> int:
        return self._year
    @year.setter
    def year(self, value: int) -> None:
        value = int(value)
        if value < 0 or value > date.today().year + 1:
            raise ValueError("Некорректный год издания")
        self._year = value

    @property
    def genre(self) -> str:
        return self._genre
    @genre.setter
    def genre(self, value: str) -> None:
        self._genre = str(value).strip() or "Не указан"

    @property
    def isbn(self) -> str:
        return self._isbn
    @isbn.setter
    def isbn(self, value: str) -> None:
        self._isbn = str(value).strip()

    @property
    def status(self) -> str:
        return self._status
    @status.setter
    def status(self, value: str) -> None:
        if value not in self.VALID_STATUSES:
            raise ValueError("Статус должен быть «В библиотеке» или «Выдана»")
        self._status = value

    @property
    def borrower(self) -> str:
        return self._borrower
    @borrower.setter
    def borrower(self, value: str) -> None:
        self._borrower = str(value).strip()

    def issue_to(self, borrower: str) -> None:
        borrower = str(borrower).strip()
        if not borrower:
            raise ValueError("Укажите имя читателя")
        if self.status == "Выдана":
            raise ValueError("Эта книга уже выдана")
        self.status = "Выдана"
        self.borrower = borrower

    def return_to_library(self) -> None:
        self.status = "В библиотеке"
        self.borrower = ""

    def to_dict(self) -> dict:
        return {"id": self.id, "title": self.title, "author": self.author,
                "year": self.year, "genre": self.genre, "isbn": self.isbn,
                "status": self.status, "borrower": self.borrower}

    @classmethod
    def from_dict(cls, data: dict) -> "Book":
        return cls(data["id"], data["title"], data["author"], data["year"],
                   data.get("genre", "Не указан"), data.get("isbn", ""),
                   data.get("status", "В библиотеке"), data.get("borrower", ""))

    def display_name(self) -> str:
        return f"{self.title} — {self.author}"

    def __str__(self) -> str:
        return self.display_name()

    def __repr__(self) -> str:
        return f"Book(id={self.id!r}, title={self.title!r}, author={self.author!r})"

    def __eq__(self, other) -> bool:
        return isinstance(other, Book) and self.id == other.id

    def __lt__(self, other) -> bool:
        if not isinstance(other, Book):
            return NotImplemented
        return (self.title.casefold(), self.author.casefold()) < (other.title.casefold(), other.author.casefold())
