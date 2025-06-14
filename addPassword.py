from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSpacerItem, QSizePolicy, QMessageBox, QGroupBox, QToolButton
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QFont, QIcon
import os
import hashlib
from styles.themes import THEMES
from auth.password_manager import PasswordManager


class SkipButton(QPushButton):
    def __init__(self, *args, theme="default", **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet(THEMES[theme]["SKIP_BUTTON_STYLES"])


class ContinueButton(QPushButton):
    def __init__(self, *args, theme="default", **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet(THEMES[theme]["CONTINUE_BUTTON_STYLES"])


class AuthWidget(QWidget):
    accepted = pyqtSignal()
    skipped = pyqtSignal()

    def __init__(self, username="", is_first_launch=False, is_password_change=False, main_window=None, theme="default"):
        super().__init__()
        if main_window is None:
            raise ValueError("main_window не может быть None")

        self.is_first_launch = is_first_launch
        self.is_password_change = is_password_change
        self.main_window = main_window
        self._message_label = None
        self.current_theme = theme

        # Определяем пути к иконкам в зависимости от темы
        self.eye_open_icon = "styles/images/cyberpunk/eye1.png" if theme == "cyberpunk" else "icons/eye1.png"
        self.eye_closed_icon = "styles/images/cyberpunk/eye2.png" if theme == "cyberpunk" else "icons/eye2.png"

        self.setStyleSheet(THEMES[self.current_theme]["AUTH_STYLES"])

        # Определяем тексты в зависимости от темы
        self.texts = {
            "default": {
                "welcome": "WELCOME!",
                "change_creds": "Изменение учетных данных",
                "username_placeholder": "Имя пользователя",
                "pin_placeholder": "PIN",
                "confirm_pin_placeholder": "Подтвердите PIN",
                "continue_btn": "Continue",
                "save_btn": "Сохранить",
                "skip_btn": "skip",
                "back_btn": "Назад",
                "error_username": "Введите имя пользователя",
                "error_pin": "Введите PIN-код",
                "error_pin_length": "PIN-код должен содержать минимум 4 символа",
                "error_pin_chars": "PIN-код должен содержать только буквы и цифры",
                "error_pin_simple": "PIN-код слишком простой. Используйте разные цифры",
                "error_pin_match": "PIN-коды не совпадают",
                "error_user_exists": "Пользователь с таким именем уже существует"
            },
            "cyberpunk": {
                "welcome": "WELCOME, CHOOMBA!",
                "change_creds": "JACK IN TO CHANGE YOUR CREDS",
                "username_placeholder": "NETRUNNER ID",
                "pin_placeholder": "ACCESS CODE",
                "confirm_pin_placeholder": "VERIFY ACCESS CODE",
                "continue_btn": "CONNECT",
                "save_btn": "UPLOAD NEW CREDS",
                "skip_btn": "GHOST MODE",
                "back_btn": "JACK OUT",
                "error_username": "NETRUNNER ID REQUIRED, CHOOMBA!",
                "error_pin": "ACCESS CODE MISSING - SECURITY BREACH IMMINENT!",
                "error_pin_length": "ACCESS CODE TOO WEAK - MINIMUM 4 DIGITS REQUIRED!",
                "error_pin_chars": "INVALID CODE FORMAT - USE ALPHANUMERIC ONLY!",
                "error_pin_simple": "WEAK ACCESS CODE DETECTED - USE DIFFERENT DIGITS!",
                "error_pin_match": "ACCESS CODES DON'T MATCH - CHECK YOUR DATA!",
                "error_user_exists": "NETRUNNER ID ALREADY IN USE - CHOOSE ANOTHER!"
            }
        }

        # Используем тексты по умолчанию, если тема не найдена
        self.current_texts = self.texts.get(self.current_theme, self.texts["default"])

        self.init_ui(username)

    def init_ui(self, username):
        # Создаем основной layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Создаем центральный контейнер с фиксированной шириной
        central_widget = QWidget()
        central_widget.setFixedWidth(300)
        central_layout = QVBoxLayout(central_widget)
        central_layout.setContentsMargins(30, 30, 30, 30)
        central_layout.setSpacing(0)

        # Иконка входа
        login_icon = QLabel()
        icon_path = f"styles/images/{self.current_theme}/login.png"
        print(f"Loading icon from: {icon_path}")  # Отладочный вывод
        print(f"Current theme: {self.current_theme}")  # Отладочный вывод

        if os.path.exists(icon_path):
            print(f"Icon file exists at: {icon_path}")  # Отладочный вывод
            icon = QIcon(icon_path)
            if not icon.isNull():
                print("Icon loaded successfully")  # Отладочный вывод
                pixmap = icon.pixmap(QSize(64, 64))
                if not pixmap.isNull():
                    print("Pixmap created successfully")  # Отладочный вывод
                    login_icon.setPixmap(pixmap)
                else:
                    print(f"Failed to create pixmap from icon: {icon_path}")
            else:
                print(f"Failed to load icon: {icon_path}")
        else:
            print(f"Icon file not found at: {os.path.abspath(icon_path)}")  # Показываем полный путь

        central_layout.addWidget(login_icon, alignment=Qt.AlignmentFlag.AlignCenter)

        # Добавляем отступ после иконки
        central_layout.addItem(QSpacerItem(0, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

        # Заголовок
        self.title = QLabel(self.current_texts["welcome"])
        if self.is_password_change:
            self.title.setText(self.current_texts["change_creds"])
        self.title.setObjectName("titleLabel")
        central_layout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignCenter)

        # Добавляем отступ после заголовка
        central_layout.addItem(QSpacerItem(0, 25, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

        # Поле для имени пользователя
        self.username_input = QLineEdit(username)
        self.username_input.setPlaceholderText(self.current_texts["username_placeholder"])
        central_layout.addWidget(self.username_input)

        # Фиксированный отступ между полями
        central_layout.addItem(QSpacerItem(0, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

        # PIN-код
        self.pin_input = QLineEdit()
        self.pin_input.setPlaceholderText(self.current_texts["pin_placeholder"])
        self.pin_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pin_input.setStyleSheet("""
            QLineEdit {
                padding-right: 35px;
            }
        """)
        central_layout.addWidget(self.pin_input)

        # Кнопка видимости PIN
        self.toggle_pin_btn = QToolButton(self.pin_input)
        self.toggle_pin_btn.setIcon(QIcon(self.eye_closed_icon))
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
            central_layout.addItem(QSpacerItem(0, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

            self.confirm_pin_input = QLineEdit()
            self.confirm_pin_input.setPlaceholderText(self.current_texts["confirm_pin_placeholder"])
            self.confirm_pin_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.confirm_pin_input.setStyleSheet("""
                QLineEdit {
                    padding-right: 35px;
                }
            """)
            central_layout.addWidget(self.confirm_pin_input)

        # Добавляем отступ перед кнопками
        central_layout.addItem(QSpacerItem(0, 30, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

        # Кнопки
        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)

        # Кнопка продолжения
        self.continue_btn = ContinueButton(self.current_texts["continue_btn"], theme=self.current_theme)
        self.continue_btn.setObjectName("continue-btn")
        if self.is_password_change:
            self.continue_btn.setText(self.current_texts["save_btn"])
        self.continue_btn.clicked.connect(self.validate_and_accept)
        button_layout.addWidget(self.continue_btn)

        # Кнопка "Skip" только при первом запуске
        if self.is_first_launch:
            self.skip_btn = SkipButton(self.current_texts["skip_btn"], theme=self.current_theme)
            self.skip_btn.clicked.connect(self.skip_auth)
            button_layout.addWidget(self.skip_btn)

        # Кнопка "Back" при смене пароля
        if self.is_password_change:
            self.back_btn = SkipButton(self.current_texts["back_btn"], theme=self.current_theme)
            self.back_btn.clicked.connect(self.go_back)
            button_layout.addWidget(self.back_btn)

        central_layout.addWidget(button_container)

        # Добавляем центральный виджет в основной layout с выравниванием по центру
        main_layout.addStretch()
        main_layout.addWidget(central_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addStretch()

    def show_error(self, message, duration=3000):
        if not self._message_label:
            self._message_label = QLabel(self)
            self._message_label.setStyleSheet("""
                QLabel {
                    background-color: #cc3333;
                    color: white;
                    padding: 10px 16px;
                    border-radius: 6px;
                    font-size: 12px;
                }
            """)
            self._message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._message_label.hide()

        self._message_label.setText(message)
        self._message_label.adjustSize()

        # Позиционируем сообщение внизу по центру
        x = (self.width() - self._message_label.width()) // 2
        y = self.height() - self._message_label.height() - 30
        self._message_label.move(x, y)
        self._message_label.show()

        # Скрываем сообщение через duration миллисекунд
        QTimer.singleShot(duration, self._message_label.hide)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._message_label and not self._message_label.isHidden():
            # Обновляем позицию сообщения при изменении размера окна
            x = (self.width() - self._message_label.width()) // 2
            y = self.height() - self._message_label.height() - 30
            self._message_label.move(x, y)

    def validate_and_accept(self):
        """Проверяет введенные данные и эмитит сигнал accepted"""
        username = self.username_input.text().strip()
        pin = self.pin_input.text().strip()

        if not username:
            self.show_error(self.current_texts["error_username"])
            return

        if not pin:
            self.show_error(self.current_texts["error_pin"])
            return

        # Проверка длины PIN-кода
        if len(pin) < 4:
            self.show_error(self.current_texts["error_pin_length"])
            return

        # Проверка на допустимые символы
        if not pin.isalnum():
            self.show_error(self.current_texts["error_pin_chars"])
            return

        # Проверка на сложность PIN-кода
        if pin.isdigit() and len(set(pin)) < 3:
            self.show_error(self.current_texts["error_pin_simple"])
            return

        if hasattr(self, 'confirm_pin_input'):
            confirm_pin = self.confirm_pin_input.text().strip()
            if pin != confirm_pin:
                self.show_error(self.current_texts["error_pin_match"])
                return

        try:
            if self.is_password_change:
                # Если это смена пароля, сначала проверяем изменение имени пользователя
                old_username = self.main_window.user_credentials.get_saved_username()
                if username != old_username:
                    if PasswordManager.vault_exists(username):
                        self.main_window.show_temporary_message(self.current_texts["error_user_exists"])
                        return

                # Очищаем старые учетные данные перед сменой пароля
                self.main_window.user_credentials.clear_old_credentials()

                # Меняем пароль в менеджере
                if not self.main_window.password_manager.change_password(pin):
                    raise Exception("Ошибка при смене пароля")

                # Если имя пользователя изменилось, меняем его
                if old_username != username:
                    if not self.main_window.password_manager.change_username(username):
                        raise Exception("Ошибка при смене имени пользователя")
            else:
                # Если это первый вход или регистрация
                # Проверяем, существует ли уже хранилище с таким именем
                if PasswordManager.vault_exists(username):
                    # Проверяем учетные данные
                    if not self.main_window.user_credentials.verify_credentials(username, pin):
                        self.show_error("Неверный PIN-код")
                        return
                    # Если учетные данные верны, создаем менеджер паролей
                    self.main_window.password_manager = PasswordManager(username, pin)
                else:
                    # Сохраняем учетные данные
                    self.main_window.user_credentials.save_credentials(username, pin)
                    # Создаем менеджер паролей
                    self.main_window.password_manager = PasswordManager(username, pin)

            # Эмитим сигнал успешной регистрации/изменения
            self.accepted.emit()

        except Exception as e:
            self.show_error(f"Ошибка: {str(e)}")
            return

    def get_credentials(self):
        return self.username_input.text().strip(), self.pin_input.text().strip()

    def skip_auth(self):
        self.skipped.emit()

    def go_back(self):
        if self.main_window:
            self.main_window.main_stack.setCurrentIndex(0)

    def show_validation_error(self, message, duration=3000):
        """Показывает сообщение об ошибке валидации"""
        if not self._message_label:
            self._message_label = QLabel(self)
            self._message_label.setStyleSheet("""
                QLabel {
                    background-color: #cc3333;
                    color: white;
                    padding: 10px 16px;
                    border-radius: 6px;
                    font-size: 12px;
                }
            """)
            self._message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._message_label.hide()

        self._message_label.setText(message)
        self._message_label.adjustSize()

        # Позиционируем сообщение внизу по центру
        x = (self.width() - self._message_label.width()) // 2
        y = self.height() - self._message_label.height() - 30
        self._message_label.move(x, y)
        self._message_label.show()

        # Скрываем сообщение через duration миллисекунд
        QTimer.singleShot(duration, self._message_label.hide)

    def toggle_password_visibility(self, input_field):
        """Переключает видимость пароля в полях ввода PIN-кода"""
        is_password_visible = input_field.echoMode() == QLineEdit.EchoMode.Password
        new_mode = QLineEdit.EchoMode.Normal if is_password_visible else QLineEdit.EchoMode.Password
        new_icon = QIcon(self.eye_open_icon if is_password_visible else self.eye_closed_icon)

        # Изменяем режим отображения для обоих полей
        self.pin_input.setEchoMode(new_mode)
        if hasattr(self, 'confirm_pin_input'):
            self.confirm_pin_input.setEchoMode(new_mode)

        # Обновляем иконку
        self.toggle_pin_btn.setIcon(new_icon)

    def update_theme(self, new_theme):
        """Обновляет тему виджета и все связанные тексты"""
        self.current_theme = new_theme
        self.setStyleSheet(THEMES[self.current_theme]["AUTH_STYLES"])

        # Обновляем пути к иконкам
        self.eye_open_icon = "styles/images/cyberpunk/eye1.png" if new_theme == "cyberpunk" else "icons/eye1.png"
        self.eye_closed_icon = "styles/images/cyberpunk/eye2.png" if new_theme == "cyberpunk" else "icons/eye2.png"

        # Обновляем иконку в соответствии с текущим состоянием
        is_password_visible = self.pin_input.echoMode() == QLineEdit.EchoMode.Normal
        new_icon = QIcon(self.eye_open_icon if is_password_visible else self.eye_closed_icon)
        self.toggle_pin_btn.setIcon(new_icon)

        # Обновляем тексты
        self.current_texts = self.texts.get(self.current_theme, self.texts["default"])

        # Обновляем все тексты в интерфейсе
        if hasattr(self, 'title'):
            if self.is_password_change:
                self.title.setText(self.current_texts["change_creds"])
            else:
                self.title.setText(self.current_texts["welcome"])

        if hasattr(self, 'username_input'):
            self.username_input.setPlaceholderText(self.current_texts["username_placeholder"])

        if hasattr(self, 'pin_input'):
            self.pin_input.setPlaceholderText(self.current_texts["pin_placeholder"])

        if hasattr(self, 'confirm_pin_input'):
            self.confirm_pin_input.setPlaceholderText(self.current_texts["confirm_pin_placeholder"])

        if hasattr(self, 'continue_btn'):
            if self.is_password_change:
                self.continue_btn.setText(self.current_texts["save_btn"])
            else:
                self.continue_btn.setText(self.current_texts["continue_btn"])

        if hasattr(self, 'skip_btn'):
            self.skip_btn.setText(self.current_texts["skip_btn"])

        if hasattr(self, 'back_btn'):
            self.back_btn.setText(self.current_texts["back_btn"])

        # Обновляем иконку входа
        icon_path = f"styles/images/{self.current_theme}/login.png"
        print(f"Updating icon to: {icon_path}")  # Отладочный вывод

        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            if not icon.isNull():
                # Определяем размер иконки в зависимости от темы
                if new_theme == "cyberpunk":
                    size = QSize(80, 80)  # Меньший размер для киберпанк темы
                else:
                    size = QSize(64, 64)  # Стандартный размер для других тем

                pixmap = icon.pixmap(size)
                if not pixmap.isNull():
                    # Находим QLabel с иконкой
                    for child in self.findChildren(QLabel):
                        if child.pixmap() is not None:
                            child.setPixmap(pixmap)
                            # Устанавливаем фиксированный размер
                            child.setFixedSize(size)
                            break

        # Обновляем стили кнопок
        if hasattr(self, 'skip_btn'):
            self.skip_btn.setStyleSheet(THEMES[self.current_theme]["SKIP_BUTTON_STYLES"])
        if hasattr(self, 'back_btn'):
            self.back_btn.setStyleSheet(THEMES[self.current_theme]["SKIP_BUTTON_STYLES"])
        if hasattr(self, 'continue_btn'):
            self.continue_btn.setStyleSheet(THEMES[self.current_theme]["CONTINUE_BUTTON_STYLES"])