from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QTextEdit,
    QPushButton, QLabel, QHBoxLayout, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon

class RightPanel(QWidget):
    save_clicked = pyqtSignal(dict)
    password_visibility_changed = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("RightPanel")
        self.password_visible = False
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Сервис
        service_label = QLabel("Сервис:")
        self.service_input = QLineEdit()
        layout.addWidget(service_label)
        layout.addWidget(self.service_input)

        # Логин
        login_label = QLabel("Логин:")
        self.login_input = QLineEdit()
        layout.addWidget(login_label)
        layout.addWidget(self.login_input)

        # Пароль с кнопкой видимости
        password_container = QWidget()
        password_layout = QHBoxLayout(password_container)
        password_layout.setContentsMargins(0, 0, 0, 0)

        password_label = QLabel("Пароль:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.toggle_password_btn = QPushButton()
        self.toggle_password_btn.setIcon(QIcon("icons/eye1.png"))
        self.toggle_password_btn.clicked.connect(self.toggle_password_visibility)
        
        password_layout.addWidget(self.password_input)
        password_layout.addWidget(self.toggle_password_btn)

        layout.addWidget(password_label)
        layout.addWidget(password_container)

        # URL
        url_label = QLabel("URL:")
        self.url_input = QLineEdit()
        layout.addWidget(url_label)
        layout.addWidget(self.url_input)

        # Заметки
        notes_label = QLabel("Заметки:")
        self.notes_input = QTextEdit()
        layout.addWidget(notes_label)
        layout.addWidget(self.notes_input)

        # Кнопка сохранения
        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self._on_save_clicked)
        layout.addWidget(self.save_button)

        layout.addStretch()

    def set_password_data(self, data):
        self.service_input.setText(data.get("service", ""))
        self.login_input.setText(data.get("login", ""))
        self.password_input.setText(data.get("password", ""))
        self.url_input.setText(data.get("url", ""))
        self.notes_input.setText(data.get("notes", ""))

    def clear_fields(self):
        self.service_input.clear()
        self.login_input.clear()
        self.password_input.clear()
        self.url_input.clear()
        self.notes_input.clear()

    def toggle_password_visibility(self):
        self.password_visible = not self.password_visible
        self.password_input.setEchoMode(
            QLineEdit.EchoMode.Normal if self.password_visible 
            else QLineEdit.EchoMode.Password
        )
        self.toggle_password_btn.setIcon(
            QIcon("icons/eye2.png" if self.password_visible else "icons/eye1.png")
        )
        self.password_visibility_changed.emit(self.password_visible)

    def _on_save_clicked(self):
        data = {
            "service": self.service_input.text(),
            "login": self.login_input.text(),
            "password": self.password_input.text(),
            "url": self.url_input.text(),
            "notes": self.notes_input.toPlainText()
        }
        self.save_clicked.emit(data) 