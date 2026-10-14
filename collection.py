
import json
from pathlib import Path
from typing import Iterable, Iterator, Optional
from models import Book

class LibraryCollection:

    def __init__(self, books: Optional[Iterable[Book]] = None):
        self._books = []
        for book in books or []:
            self.add(book)

    def add(self, book: Book) -> None:
        if not isinstance(book, Book):
            raise TypeError("В библиотеку можно добавлять только объекты Book")
        if self.find_by_id(book.id):
            raise ValueError("Книга с таким идентификатором уже существует")
        self._books.append(book)

    def remove(self, book_id: str) -> Book:
        book = self.find_by_id(book_id)
        if book is None:
            raise KeyError("Книга не найдена")
        self._books.remove(book)
        return book

    def find_by_id(self, book_id: str) -> Optional[Book]:
        for book in self._books:
            if book.id == str(book_id):
                return book
        return None

    def search(self, query: str = "", status: str = "Все") -> list[Book]:
        query = query.casefold().strip()
        result = []
        for book in self._books:
            searchable = f"{book.title} {book.author} {book.genre} {book.isbn} {book.year}".casefold()
            if query and query not in searchable:
                continue
            if status != "Все" and book.status != status:
                continue
            result.append(book)
        return sorted(result)

    def statistics(self) -> tuple[int, int, int]:
        total = len(self._books)
        issued = sum(book.status == "Выдана" for book in self._books)
        return total, total - issued, issued

    def save_json(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = [book.to_dict() for book in self._books]
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        temporary.replace(path)

    @classmethod
    def load_json(cls, path: str | Path) -> "LibraryCollection":
        path = Path(path)
        if not path.exists():
            return cls()
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            raise ValueError("Ожидался список книг в JSON-файле")
        return cls(Book.from_dict(item) for item in raw)

    def __len__(self) -> int:
        return len(self._books)

    def __iter__(self) -> Iterator[Book]:
        return iter(self._books)

    def __contains__(self, book: object) -> bool:
        return book in self._books

    def __getitem__(self, index: int) -> Book:
        return self._books[index]
