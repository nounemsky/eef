import string
import secrets
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QCheckBox, QPushButton, QLineEdit, QMessageBox, QProgressBar, QWidget
)
from PyQt6.QtCore import Qt
from styles import PASSWORD_GENERATOR_STYLES, DIALOG_TITLE_BAR_STYLES, APP_STYLES


class TitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._drag_pos = None
        self.setFixedHeight(18)
        self.setStyleSheet(DIALOG_TITLE_BAR_STYLES)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 8, 0)

        self.close_btn = QPushButton("")
        self.close_btn.setFixedSize(16, 16)
        self.close_btn.clicked.connect(self.parent().close)

        layout.addWidget(self.close_btn)
        layout.addStretch()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.parent().frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos:
            self.parent().move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()


class PasswordGeneratorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setGeometry(400, 200, 400, 280)
        self.setStyleSheet(PASSWORD_GENERATOR_STYLES)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.title_bar = TitleBar(self)
        layout.addWidget(self.title_bar)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        length_layout = QHBoxLayout()
        self.length_combo = QComboBox()
        presets = ["8", "12", "16", "20", "24", "32"]
        self.length_combo.addItems(presets)
        self.length_combo.setCurrentText("16")
        length_layout.addWidget(self.length_combo)
        main_layout.addLayout(length_layout)

        # Чекбоксы
        self.include_basic = QCheckBox("Буквы и цифры", checked=True)
        self.include_symbols = QCheckBox("Спецсимволы (!@#$%^&*)", checked=True)
        self.exclude_similar = QCheckBox("Исключать похожие символы (1lI0Oo)", checked=True)

        main_layout.addWidget(self.include_basic)
        main_layout.addWidget(self.include_symbols)
        main_layout.addWidget(self.exclude_similar)

        self.preview = QLineEdit()
        self.preview.setReadOnly(True)
        main_layout.addWidget(self.preview)

        self.strength_bar = QProgressBar()
        self.strength_bar.setTextVisible(False)
        self.strength_bar.setFixedHeight(5)
        self.strength_bar.setRange(0, 100)
        self.strength_bar.setStyleSheet(APP_STYLES)
        main_layout.addWidget(self.strength_bar)

        btn_layout = QHBoxLayout()
        self.generate_btn = QPushButton("Сгенерировать", clicked=self.generate)
        self.accept_btn = QPushButton("Использовать", clicked=self.accept)
        btn_layout.addWidget(self.generate_btn)
        btn_layout.addWidget(self.accept_btn)
        main_layout.addLayout(btn_layout)

        layout.addLayout(main_layout)
        self.setLayout(layout)

        # Подключаем сигналы к генерации для живого обновления
        self.length_combo.currentTextChanged.connect(self.generate)
        self.include_basic.stateChanged.connect(self.generate)
        self.include_symbols.stateChanged.connect(self.generate)
        self.exclude_similar.stateChanged.connect(self.generate)

        self.generate()

    def generate(self):
        chars = ''
        if self.include_basic.isChecked():
            chars += string.ascii_letters + string.digits
        if self.include_symbols.isChecked():
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?~"
        if self.exclude_similar.isChecked():
            chars = chars.translate(str.maketrans('', '', '1lI0Oo'))

        if not chars:
            QMessageBox.warning(self, "Ошибка", "Выберите хотя бы один тип символов!")
            return

        try:
            length = int(self.length_combo.currentText())
            password = ''.join(secrets.choice(chars) for _ in range(length))
            self.preview.setText(password)

            strength = self.evaluate_strength(password)
            self.strength_bar.setValue(strength)

            if strength < 40:
                color = "#d32f2f"  # красный
            elif strength < 70:
                color = "#fbc02d"  # жёлтый
            else:
                color = "#00c853"  # зелёный

            self.strength_bar.setStyleSheet(f"""
                QProgressBar {{
                    background-color: #333;
                    border: none;
                    border-radius: 2px;
                }}
                QProgressBar::chunk {{
                    background-color: {color};
                    border-radius: 2px;
                }}
            """)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сгенерировать пароль: {str(e)}")

    def evaluate_strength(self, password: str) -> int:
        length_score = min(len(password), 20) * 5
        variety_score = 0
        if any(c.islower() for c in password):
            variety_score += 1
        if any(c.isupper() for c in password):
            variety_score += 1
        if any(c.isdigit() for c in password):
            variety_score += 1
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?~" for c in password):
            variety_score += 1
        return min(length_score + variety_score * 5, 100)

    def get_password(self):
        return self.preview.text()
