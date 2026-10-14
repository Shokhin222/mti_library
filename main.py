
import sys
from PyQt6.QtWidgets import QApplication, QDialog, QMessageBox
from PyQt6.QtGui import QFont
from windows import LoginDialog, MainWindow
from collection import LibraryCollection
from report import SessionReporter
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
DATA_FILE = APP_DIR / "data" / "books.json"
REPORT_FILE = APP_DIR / "report.txt"

DARK_STYLE = """
QWidget { background: #171a21; color: #e8eaf0; font-family: Segoe UI, Arial; font-size: 10pt; }
QMainWindow, QDialog { background: #171a21; }
QLabel#title { font-size: 20pt; font-weight: 700; color: #f4f6fb; }
QLabel#muted { color: #9aa4b2; }
QLineEdit, QComboBox, QSpinBox, QDateEdit, QTextEdit {
    background: #232833; border: 1px solid #3b4352; border-radius: 6px;
    padding: 7px; selection-background-color: #4778d9;
}
QComboBox QAbstractItemView { background: #232833; selection-background-color: #355ea8; }
QPushButton {
    background: #2c3442; border: 1px solid #414b5d; border-radius: 6px;
    padding: 8px 12px; color: #f3f5f9;
}
QPushButton:hover { background: #394457; }
QPushButton#primary { background: #356bd6; border-color: #356bd6; font-weight: 600; }
QPushButton#primary:hover { background: #477ce8; }
QPushButton#danger { background: #7d3039; border-color: #9d3b47; }
QTableWidget { background: #20242d; alternate-background-color: #252a35; gridline-color: #343b49; border: 1px solid #353d4b; }
QHeaderView::section { background: #2b313d; color: #dce2eb; padding: 8px; border: 0; border-bottom: 1px solid #414958; }
QTableWidget::item { padding: 5px; }
QTableWidget::item:selected { background: #31599b; }
QStatusBar { background: #20242d; color: #9aa4b2; }
QMenuBar, QMenu { background: #20242d; color: #e8eaf0; }
QMenu::item:selected { background: #355ea8; }
QGroupBox { border: 1px solid #343b49; border-radius: 8px; margin-top: 10px; padding-top: 8px; }
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; color: #aeb9c9; }
"""

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Библиотека")
    app.setFont(QFont("Segoe UI", 10))
    app.setStyleSheet(DARK_STYLE)

    reporter = SessionReporter(REPORT_FILE)
    reporter.start()
    login = LoginDialog()
    if login.exec() != QDialog.DialogCode.Accepted:
        reporter.finish("Отменён")
        return 0

    try:
        library = LibraryCollection.load_json(DATA_FILE)
    except (OSError, ValueError, TypeError) as exc:
        QMessageBox.critical(None, "Ошибка данных", f"Не удалось загрузить каталог:\n{exc}")
        library = LibraryCollection()

    window = MainWindow(library, DATA_FILE, login.username, reporter)
    window.show()
    result = app.exec()
    return result

if __name__ == "__main__":
    sys.exit(main())
