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
        self.setStyleSheet(THEMES[self.current_theme]["AUTH_STYLES"])
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
        title = QLabel("WELCOME!")
        if self.is_password_change:
            title.setText("Изменение учетных данных")
        title.setObjectName("titleLabel")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        central_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Добавляем отступ после заголовка
        central_layout.addItem(QSpacerItem(0, 25, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

        # Поле для имени пользователя
        self.username_input = QLineEdit(username)
        self.username_input.setPlaceholderText("Имя пользователя")
        central_layout.addWidget(self.username_input)
        
        # Фиксированный отступ между полями
        central_layout.addItem(QSpacerItem(0, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

        # PIN-код
        self.pin_input = QLineEdit()
        self.pin_input.setPlaceholderText("PIN")
        self.pin_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pin_input.setStyleSheet("""
            QLineEdit {
                padding-right: 35px;
            }
        """)
        central_layout.addWidget(self.pin_input)

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
            central_layout.addItem(QSpacerItem(0, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
            
            self.confirm_pin_input = QLineEdit()
            self.confirm_pin_input.setPlaceholderText("Подтвердите PIN")
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
        self.continue_btn = ContinueButton("Continue", theme=self.current_theme)
        self.continue_btn.setObjectName("continue-btn")
        if self.is_password_change:
            self.continue_btn.setText("Сохранить")
        self.continue_btn.clicked.connect(self.validate_and_accept)
        button_layout.addWidget(self.continue_btn)

        # Кнопка "Skip" только при первом запуске
        if self.is_first_launch:
            self.skip_btn = SkipButton("skip", theme=self.current_theme)
            self.skip_btn.clicked.connect(self.skip_auth)
            button_layout.addWidget(self.skip_btn)

        # Кнопка "Back" при смене пароля
        if self.is_password_change:
            self.back_btn = SkipButton("Назад", theme=self.current_theme)
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
            self.show_error("Введите имя пользователя")
            return

        if not pin:
            self.show_error("Введите PIN-код")
            return

        # Проверка длины PIN-кода
        if len(pin) < 4:
            self.show_error("PIN-код должен содержать минимум 4 символа")
            return
            
        # Проверка на допустимые символы
        if not pin.isalnum():
            self.show_error("PIN-код должен содержать только буквы и цифры")
            return
            
        # Проверка на сложность PIN-кода
        if pin.isdigit() and len(set(pin)) < 3:
            self.show_error("PIN-код слишком простой. Используйте разные цифры")
            return

        if hasattr(self, 'confirm_pin_input'):
            confirm_pin = self.confirm_pin_input.text().strip()
            if pin != confirm_pin:
                self.show_error("PIN-коды не совпадают")
                return

        try:
            if self.is_password_change:
                # Если это смена пароля, сначала проверяем изменение имени пользователя
                old_username = self.main_window.user_credentials.get_saved_username()
                if username != old_username:
                    if PasswordManager.vault_exists(username):
                        self.main_window.show_temporary_message("Пользователь с таким именем уже существует")
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
                    if self.main_window.user_credentials.verify_credentials(username, pin):
                        # Если учетные данные верны, создаем менеджер паролей
                        self.main_window.password_manager = PasswordManager(username, pin)
                    else:
                        # Если пароль неверный, показываем уведомление
                        self.main_window.show_temporary_message("Неверный PIN-код")
                        return
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

    def save_password(self):
        """Сохраняет новый пароль или обновляет существующий"""
        service = self.service_input.text().strip()
        login = self.login_input.text().strip()
        password = self.password_input.text().strip()
        url = self.url_input.text().strip()
        email = self.email_input.text().strip()
        phone = self.phone_input.text().strip()
        notes = self.notes_input.toPlainText().strip()

        try:
            # Только заполненные поля попадут в kwargs
            kwargs = {}
            if url: kwargs["url"] = url
            if email: kwargs["email"] = email
            if phone: kwargs["phone"] = phone
            if notes: kwargs["notes"] = notes

            self.password_manager.save_password(
                service=service,
                password=password,
                login=login,
                **kwargs
            )
            self.passwords = self.password_manager.passwords
            self.update_list()
            self.clear_fields()
            self.show_validation_error("Пароль успешно сохранен", duration=2000)
        except ValueError as e:
            # Показываем ошибку валидации
            self.show_validation_error(str(e))
        except Exception as e:
            error_msg = f"Ошибка сохранения: {str(e)}"
            print(error_msg)
            QMessageBox.critical(self, "Ошибка", error_msg)

    def toggle_password_visibility(self, input_field):
        """Переключает видимость пароля в полях ввода PIN-кода"""
        is_password_visible = input_field.echoMode() == QLineEdit.EchoMode.Password
        new_mode = QLineEdit.EchoMode.Normal if is_password_visible else QLineEdit.EchoMode.Password
        new_icon = QIcon("icons/eye1.png") if is_password_visible else QIcon("icons/eye2.png")
        
        # Изменяем режим отображения для обоих полей
        self.pin_input.setEchoMode(new_mode)
        if hasattr(self, 'confirm_pin_input'):
            self.confirm_pin_input.setEchoMode(new_mode)
        
        # Обновляем иконку
        self.toggle_pin_btn.setIcon(new_icon)

    def update_theme(self, new_theme):
        """Обновляет тему виджета"""
        self.current_theme = new_theme
        self.setStyleSheet(THEMES[self.current_theme]["AUTH_STYLES"])
        
        # Обновляем иконку входа
        icon_path = f"styles/images/{self.current_theme}/login.png"
        print(f"Updating icon to: {icon_path}")  # Отладочный вывод
        
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            if not icon.isNull():
                pixmap = icon.pixmap(QSize(64, 64))
                if not pixmap.isNull():
                    # Находим QLabel с иконкой
                    for child in self.findChildren(QLabel):
                        if child.pixmap() is not None:
                            child.setPixmap(pixmap)
                            break
        
        # Обновляем стили кнопок
        if hasattr(self, 'skip_btn'):
            self.skip_btn.setStyleSheet(THEMES[self.current_theme]["SKIP_BUTTON_STYLES"])
        if hasattr(self, 'back_btn'):
            self.back_btn.setStyleSheet(THEMES[self.current_theme]["SKIP_BUTTON_STYLES"])
        if hasattr(self, 'continue_btn'):
            self.continue_btn.setStyleSheet(THEMES[self.current_theme]["CONTINUE_BUTTON_STYLES"])
