from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSpacerItem, QSizePolicy, QMessageBox, QToolButton
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QFont, QIcon
from styles import AUTH_STYLES
import os
import hashlib


class AuthWidget(QWidget):
    accepted = pyqtSignal()
    skipped = pyqtSignal()  # Новый сигнал для пропуска

    def __init__(self, username="", is_first_launch=False, is_password_change=False, main_window=None):
        super().__init__()
        self.is_first_launch = is_first_launch
        self.is_password_change = is_password_change
        self.main_window = main_window
        self.init_ui(username)

    def init_ui(self, username):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Добавляем растягивающийся элемент сверху
        layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Центральный контейнер
        center_container = QWidget()
        center_container.setObjectName("AuthContainer")
        center_container.setStyleSheet("""
            QWidget#AuthContainer {
                background-color: transparent;
                border: none;
                border-radius: 0px;
            }
        """)
        center_layout = QVBoxLayout(center_container)
        center_layout.setContentsMargins(30, 30, 30, 30)
        center_layout.setSpacing(10)

        # Логотип
        logo_label = QLabel()
        logo_label.setPixmap(QIcon("icons/Login.png").pixmap(QSize(69, 69)))
        center_layout.addWidget(logo_label, alignment=Qt.AlignmentFlag.AlignCenter)
        center_layout.addSpacing(25)

        # Заголовок
        title = QLabel("Yooo, Welcome Back!" if not self.is_password_change else "Изменение учетных данных")
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 30px;
                font-weight: normal;
            }
        """)
        center_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        center_layout.addSpacing(15)

        # Поле для имени пользователя
        self.username_input = QLineEdit(username)
        self.username_input.setFixedWidth(250)
        self.username_input.setFixedHeight(35)
        self.username_input.setPlaceholderText("Username" if not self.is_password_change else "Username")
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                background-color: #1C1C1E;
                border: 1px solid #3D3D3D;
                border-radius: 6px;
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #666666;
            }
        """)
        center_layout.addWidget(self.username_input, alignment=Qt.AlignmentFlag.AlignCenter)

        # PIN-код
        self.pin_input = QLineEdit()
        self.pin_input.setFixedWidth(250)
        self.pin_input.setFixedHeight(35)
        self.pin_input.setPlaceholderText("PIN")
        self.pin_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pin_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                padding-right: 35px;
                background-color: #1C1C1E;
                border: 1px solid #3D3D3D;
                border-radius: 6px;
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #666666;
            }
        """)
        center_layout.addWidget(self.pin_input, alignment=Qt.AlignmentFlag.AlignCenter)

        # Кнопка видимости PIN
        self.toggle_pin_btn = QToolButton(self.pin_input)
        self.toggle_pin_btn.setIcon(QIcon("icons/eye2.png"))
        self.toggle_pin_btn.setIconSize(QSize(24, 24))
        self.toggle_pin_btn.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
                width: 20px;
                height: 20px;
            }
        """)
        self.toggle_pin_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_pin_btn.clicked.connect(lambda: self.toggle_password_visibility(self.pin_input))

        # Позиционируем кнопку внутри поля PIN
        def position_pin_button():
            self.toggle_pin_btn.move(
                self.pin_input.width() - 30,
                (self.pin_input.height() - 20) // 2
            )
        self.pin_input.resizeEvent = lambda e: position_pin_button()

        # Подтверждение PIN-кода (только при первом запуске или смене пароля)
        if self.is_first_launch or self.is_password_change:
            self.confirm_pin_input = QLineEdit()
            self.confirm_pin_input.setFixedWidth(250)
            self.confirm_pin_input.setFixedHeight(35)
            self.confirm_pin_input.setPlaceholderText("Confirm PIN" if not self.is_password_change else "Confirm PIN")
            self.confirm_pin_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.confirm_pin_input.setStyleSheet("""
                QLineEdit {
                    padding: 10px;
                    padding-right: 35px;
                    background-color: #1C1C1E;
                    border: 1px solid #3D3D3D;
                    border-radius: 6px;
                    color: white;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border: 1px solid #666666;
                }
            """)
            center_layout.addWidget(self.confirm_pin_input, alignment=Qt.AlignmentFlag.AlignCenter)

        center_layout.addSpacing(10)

        # Кнопка continue
        self.continue_btn = QPushButton("continue" if not self.is_password_change else "Сохранить")
        self.continue_btn.setFixedWidth(250)
        self.continue_btn.setFixedHeight(35)
        self.continue_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: none;
                border-radius: 6px;
                color: black;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        self.continue_btn.clicked.connect(self.validate_and_accept)
        center_layout.addWidget(self.continue_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # Кнопка SKIP только при первом запуске
        if self.is_first_launch:
            self.skip_btn = QPushButton("SKIP")
            self.skip_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    color: #666666;
                    font-size: 14px;
                    text-decoration: underline;
                }
                QPushButton:hover {
                    color: #999999;
                }
            """)
            self.skip_btn.clicked.connect(self.skip_auth)
            center_layout.addWidget(self.skip_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # Кнопка "Back" при смене пароля
        if self.is_password_change:
            self.back_btn = QPushButton("Назад")
            self.back_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    color: #666666;
                    font-size: 12px;
                }
                QPushButton:hover {
                    color: #999999;
                }
            """)
            self.back_btn.clicked.connect(self.go_back)
            center_layout.addWidget(self.back_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # Сообщение об ошибке
        self.error_label = QLabel()
        self.error_label.setStyleSheet("""
            QLabel {
                color: #ff4444;
                font-size: 12px;
            }
        """)
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        center_layout.addWidget(self.error_label)

        # Добавляем центральный контейнер в основной layout
        layout.addWidget(center_container, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Добавляем растягивающийся элемент снизу
        layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

    def toggle_password_visibility(self, input_field):
        is_password_visible = input_field.echoMode() == QLineEdit.EchoMode.Password
        new_mode = QLineEdit.EchoMode.Normal if is_password_visible else QLineEdit.EchoMode.Password
        new_icon = QIcon("icons/eye1.png") if is_password_visible else QIcon("icons/eye2.png")
        
        # Изменяем режим отображения для обоих полей
        self.pin_input.setEchoMode(new_mode)
        if hasattr(self, 'confirm_pin_input'):
            self.confirm_pin_input.setEchoMode(new_mode)
        
        # Обновляем иконку
        self.toggle_pin_btn.setIcon(new_icon)

    def validate_and_accept(self):
        username = self.username_input.text().strip()
        pin = self.pin_input.text().strip()

        if not username:
            self.show_error("Введите имя пользователя")
            return

        if not pin:
            self.show_error("Введите PIN-код")
            return

        if len(pin) < 4:
            self.show_error("PIN-код должен содержать минимум 4 символа")
            return

        if hasattr(self, 'confirm_pin_input'):
            confirm_pin = self.confirm_pin_input.text().strip()
            if pin != confirm_pin:
                self.show_error("PIN-коды не совпадают")
                return

        # Проверяем, существует ли уже хранилище с таким именем
        if self.is_password_change:
            old_username = self.main_window.user_credentials.get_saved_username()
            if username != old_username:
                vault_path = os.path.join('vaults', f'vault_{hashlib.sha256(username.encode()).hexdigest()[:8]}.dat')
                if os.path.exists(vault_path):
                    if not QMessageBox.question(
                        self,
                        "Подтверждение",
                        "Пользователь с таким именем уже существует. Хотите перезаписать его данные?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    ) == QMessageBox.StandardButton.Yes:
                        return

        self.accepted.emit()

    def show_error(self, message):
        self.error_label.setText(message)
        self.error_label.show()

    def get_credentials(self):
        return self.username_input.text().strip(), self.pin_input.text().strip()

    def skip_auth(self):
        self.skipped.emit()

    def go_back(self):
        if self.main_window:
            self.main_window.main_stack.setCurrentIndex(0)
