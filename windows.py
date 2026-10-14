
from datetime import datetime
from uuid import uuid4
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QSpinBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QInputDialog, QStatusBar,
    QGroupBox, QMenuBar, QMenu, QAbstractItemView
)
from models import Book
from widgets import StatCard

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вход в библиотеку")
        self.setFixedSize(390, 190)
        self.username = ""
        layout = QVBoxLayout(self)
        title = QLabel("Добро пожаловать")
        title.setObjectName("title")
        subtitle = QLabel("Введите имя сотрудника для начала работы")
        subtitle.setObjectName("muted")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Например, Анна")
        self.name_input.returnPressed.connect(self.accept_login)
        buttons = QHBoxLayout()
        cancel = QPushButton("Выход")
        enter = QPushButton("Войти")
        enter.setObjectName("primary")
        cancel.clicked.connect(self.reject)
        enter.clicked.connect(self.accept_login)
        buttons.addWidget(cancel)
        buttons.addWidget(enter)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.name_input)
        layout.addLayout(buttons)

    def accept_login(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Не указано имя", "Введите имя сотрудника.")
            return
        self.username = name
        self.accept()

class BookDialog(QDialog):
    def __init__(self, book: Book | None = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактирование книги" if book else "Новая книга")
        self.setMinimumWidth(420)
        self.book = book
        form = QFormLayout(self)
        self.title_input = QLineEdit(book.title if book else "")
        self.author_input = QLineEdit(book.author if book else "")
        self.year_input = QSpinBox()
        self.year_input.setRange(0, datetime.now().year + 1)
        self.year_input.setValue(book.year if book else datetime.now().year)
        self.genre_input = QLineEdit(book.genre if book else "")
        self.isbn_input = QLineEdit(book.isbn if book else "")
        self.status_input = QComboBox()
        self.status_input.addItems(Book.VALID_STATUSES)
        if book:
            self.status_input.setCurrentText(book.status)
        self.borrower_input = QLineEdit(book.borrower if book else "")
        self.borrower_input.setPlaceholderText("Если книга выдана")
        form.addRow("Название *", self.title_input)
        form.addRow("Автор *", self.author_input)
        form.addRow("Год издания", self.year_input)
        form.addRow("Жанр", self.genre_input)
        form.addRow("ISBN", self.isbn_input)
        form.addRow("Статус", self.status_input)
        form.addRow("Читатель", self.borrower_input)
        buttons = QHBoxLayout()
        save = QPushButton("Сохранить")
        save.setObjectName("primary")
        cancel = QPushButton("Отмена")
        save.clicked.connect(self.validate_and_accept)
        cancel.clicked.connect(self.reject)
        buttons.addWidget(cancel)
        buttons.addWidget(save)
        form.addRow(buttons)

    def validate_and_accept(self):
        if not self.title_input.text().strip() or not self.author_input.text().strip():
            QMessageBox.warning(self, "Проверьте поля", "Название и автор обязательны.")
            return
        if self.status_input.currentText() == "Выдана" and not self.borrower_input.text().strip():
            QMessageBox.warning(self, "Нужен читатель", "Для выданной книги укажите имя читателя.")
            return
        self.accept()

    def values(self):
        return {
            "title": self.title_input.text().strip(),
            "author": self.author_input.text().strip(),
            "year": self.year_input.value(),
            "genre": self.genre_input.text().strip() or "Не указан",
            "isbn": self.isbn_input.text().strip(),
            "status": self.status_input.currentText(),
            "borrower": self.borrower_input.text().strip() if self.status_input.currentText() == "Выдана" else "",
        }

class MainWindow(QMainWindow):
    HEADERS = ["Название", "Автор", "Жанр", "Год", "ISBN", "Статус", "Читатель"]

    def __init__(self, library, data_file, username, reporter):
        super().__init__()
        self.library = library
        self.data_file = data_file
        self.username = username
        self.reporter = reporter
        self.setWindowTitle("Библиотека — учёт книжного фонда")
        self.resize(1120, 720)
        self._build_menu()
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("Книжный фонд")
        title.setObjectName("title")
        subtitle = QLabel(f"Управление каталогом библиотеки · сотрудник: {username}")
        subtitle.setObjectName("muted")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header.addLayout(title_box)
        header.addStretch()
        self.add_button = QPushButton("+ Добавить книгу")
        self.add_button.setObjectName("primary")
        self.add_button.clicked.connect(self.add_book)
        header.addWidget(self.add_button)
        root.addLayout(header)

        stats = QHBoxLayout()
        self.total_card = StatCard("Всего книг")
        self.available_card = StatCard("В библиотеке")
        self.issued_card = StatCard("Выдано читателям")
        stats.addWidget(self.total_card)
        stats.addWidget(self.available_card)
        stats.addWidget(self.issued_card)
        root.addLayout(stats)

        search_group = QGroupBox("Поиск и фильтрация")
        search_layout = QHBoxLayout(search_group)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Название, автор, жанр, ISBN или год...")
        self.search_input.textChanged.connect(self.refresh_table)
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Все", *Book.VALID_STATUSES])
        self.status_filter.currentTextChanged.connect(self.refresh_table)
        search_layout.addWidget(QLabel("Поиск:"))
        search_layout.addWidget(self.search_input, 1)
        search_layout.addWidget(QLabel("Статус:"))
        search_layout.addWidget(self.status_filter)
        root.addWidget(search_group)

        self.table = QTableWidget(0, len(self.HEADERS))
        self.table.setHorizontalHeaderLabels(self.HEADERS)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSortingEnabled(False)
        self.table.doubleClicked.connect(self.edit_book)
        root.addWidget(self.table, 1)

        actions = QHBoxLayout()
        self.edit_button = QPushButton("Редактировать")
        self.delete_button = QPushButton("Удалить")
        self.issue_button = QPushButton("Выдать читателю")
        self.return_button = QPushButton("Принять возврат")
        self.save_button = QPushButton("Сохранить каталог")
        self.delete_button.setObjectName("danger")
        self.edit_button.clicked.connect(self.edit_book)
        self.delete_button.clicked.connect(self.delete_book)
        self.issue_button.clicked.connect(self.issue_book)
        self.return_button.clicked.connect(self.return_book)
        self.save_button.clicked.connect(self.save_catalog)
        for button in (self.edit_button, self.delete_button, self.issue_button, self.return_button):
            actions.addWidget(button)
        actions.addStretch()
        actions.addWidget(self.save_button)
        root.addLayout(actions)
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Готово")
        self.refresh_table()

    def _build_menu(self):
        bar = self.menuBar()
        file_menu = bar.addMenu("Файл")
        save_action = file_menu.addAction("Сохранить каталог")
        save_action.triggered.connect(self.save_catalog)
        file_menu.addSeparator()
        exit_action = file_menu.addAction("Выход")
        exit_action.triggered.connect(self.close)
        help_menu = bar.addMenu("Справка")
        about_action = help_menu.addAction("О программе")
        about_action.triggered.connect(self.show_about)

    def selected_book(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Книга не выбрана", "Сначала выберите строку в таблице.")
            return None
        item = self.table.item(row, 0)
        return self.library.find_by_id(item.data(Qt.ItemDataRole.UserRole))

    def refresh_table(self, *_):
        books = self.library.search(self.search_input.text() if hasattr(self, "search_input") else "",
                                    self.status_filter.currentText() if hasattr(self, "status_filter") else "Все")
        self.table.setRowCount(0)
        for book in books:
            row = self.table.rowCount()
            self.table.insertRow(row)
            values = [book.title, book.author, book.genre, str(book.year), book.isbn,
                      book.status, book.borrower or "—"]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column == 0:
                    item.setData(Qt.ItemDataRole.UserRole, book.id)
                self.table.setItem(row, column, item)
        total, available, issued = self.library.statistics()
        self.total_card.set_value(total)
        self.available_card.set_value(available)
        self.issued_card.set_value(issued)
        self.statusBar().showMessage(f"Показано: {len(books)} из {total}")

    def add_book(self):
        dialog = BookDialog(parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            values = dialog.values()
            book = Book(str(uuid4()), **values)
            self.library.add(book)
            self.save_catalog(show_message=False)
            self.refresh_table()
        except (ValueError, TypeError) as exc:
            QMessageBox.warning(self, "Не удалось добавить", str(exc))

    def edit_book(self):
        book = self.selected_book()
        if book is None:
            return
        dialog = BookDialog(book, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            values = dialog.values()
            for key, value in values.items():
                setattr(book, key, value)
            self.save_catalog(show_message=False)
            self.refresh_table()
        except (ValueError, TypeError) as exc:
            QMessageBox.warning(self, "Не удалось сохранить", str(exc))

    def delete_book(self):
        book = self.selected_book()
        if book is None:
            return
        answer = QMessageBox.question(self, "Удаление книги",
            f"Удалить «{book.title}» из каталога?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if answer == QMessageBox.StandardButton.Yes:
            self.library.remove(book.id)
            self.save_catalog(show_message=False)
            self.refresh_table()

    def issue_book(self):
        book = self.selected_book()
        if book is None:
            return
        borrower, ok = QInputDialog.getText(self, "Выдача книги", "Имя читателя:")
        if not ok:
            return
        try:
            book.issue_to(borrower)
            self.save_catalog(show_message=False)
            self.refresh_table()
        except ValueError as exc:
            QMessageBox.warning(self, "Невозможно выдать", str(exc))

    def return_book(self):
        book = self.selected_book()
        if book is None:
            return
        if book.status != "Выдана":
            QMessageBox.information(self, "Возврат", "Эта книга уже находится в библиотеке.")
            return
        book.return_to_library()
        self.save_catalog(show_message=False)
        self.refresh_table()

    def save_catalog(self, show_message=True):
        try:
            self.library.save_json(self.data_file)
            self.statusBar().showMessage("Каталог сохранён", 3000)
            if show_message:
                QMessageBox.information(self, "Сохранено", "Каталог сохранён в data/books.json.")
        except OSError as exc:
            QMessageBox.critical(self, "Ошибка сохранения", str(exc))

    def show_about(self):
        QMessageBox.about(self, "О программе",
            "Библиотека — настольное приложение учёта книжного фонда.\n"
            "Python 3.10+ · PyQt6 · JSON\n\n"
            "Данные сохраняются между запусками приложения.")

    def closeEvent(self, event):
        try:
            self.library.save_json(self.data_file)
            self.reporter.finish(self.username)
            event.accept()
        except OSError as exc:
            answer = QMessageBox.warning(self, "Ошибка сохранения",
                f"Не удалось сохранить каталог:\n{exc}\nВсё равно закрыть?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if answer == QMessageBox.StandardButton.Yes:
                self.reporter.finish(self.username)
                event.accept()
            else:
                event.ignore()
