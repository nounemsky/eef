from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QListWidget,
    QComboBox, QLabel, QHBoxLayout, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal

class LeftPanel(QWidget):
    password_selected = pyqtSignal(dict)
    search_changed = pyqtSignal(str)
    category_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("LeftPanel")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Поиск
        search_container = QWidget()
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(10, 10, 10, 0)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск...")
        self.search_input.textChanged.connect(self.search_changed.emit)
        search_layout.addWidget(self.search_input)

        layout.addWidget(search_container)

        # Категории
        category_container = QWidget()
        category_layout = QHBoxLayout(category_container)
        category_layout.setContentsMargins(10, 0, 10, 0)

        self.category_combo = QComboBox()
        self.category_combo.addItem("Все категории")
        self.category_combo.currentTextChanged.connect(self.category_changed.emit)
        category_layout.addWidget(self.category_combo)

        layout.addWidget(category_container)

        # Список паролей
        self.password_list = QListWidget()
        self.password_list.setObjectName("passwordList")
        self.password_list.itemClicked.connect(self._on_password_selected)
        layout.addWidget(self.password_list)

    def update_categories(self, categories):
        current = self.category_combo.currentText()
        self.category_combo.clear()
        self.category_combo.addItem("Все категории")
        self.category_combo.addItems(sorted(categories))
        index = self.category_combo.findText(current)
        if index >= 0:
            self.category_combo.setCurrentIndex(index)

    def update_password_list(self, passwords):
        self.password_list.clear()
        for password in passwords:
            self.password_list.addItem(password["service"])

    def _on_password_selected(self, item):
        service = item.text()
        # Emit signal with password data
        self.password_selected.emit({"service": service}) 