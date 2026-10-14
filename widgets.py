
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

class StatCard(QFrame):

    def __init__(self, caption: str, value: str = "0", parent=None):
        super().__init__(parent)
        self.setObjectName("statCard")
        self.setStyleSheet("#statCard { background:#222833; border:1px solid #343d4c; border-radius:9px; }")
        layout = QVBoxLayout(self)
        self.caption_label = QLabel(caption)
        self.caption_label.setStyleSheet("color:#a5afbf; font-size:9pt;")
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet("font-size:19pt; font-weight:700; color:#f3f6fb;")
        layout.addWidget(self.caption_label)
        layout.addWidget(self.value_label)
        layout.setContentsMargins(14, 10, 14, 10)

    def set_value(self, value: int) -> None:
        self.value_label.setText(str(value))
