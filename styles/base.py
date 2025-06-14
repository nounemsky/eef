"""Базовые стили приложения"""

# Основные стили приложения
APP_STYLES = """
#MainContainer {
    background-color: rgba(20, 20, 20, 253);
    border-radius: 8px;
    border: 1px solid #3a3a3a;
}

#CentralWidget {
    background-color: transparent;
    border-top: 1px solid #444;
    border-radius: 0px;
}

QLabel { 
    color: #ffffff; 
    font-size: 16px; 
}

QLineEdit {
    background-color: #3c3f41; 
    color: #ffffff;
    border: 1px solid #606060;
    border-radius: 4px; 
    padding: 5px;
}
QLineEdit#passwordInput {
    color: white;
    background-color: #2D2D2D;
    border-radius: 4px;
    border: 1px solid #404040;
    padding: 3px 12px;
    font-size: 14px;
}

QLineEdit#passwordInput:hover {
    background-color: #383838;
    border: 1px solid #505050;
}

QLineEdit#passwordInput:focus {
    background-color: #2D2D2D;
    border: 1px solid #ffffff;
} 
QListWidget, QComboBox {
    background-color: #3c3f41; 
    color: #ffffff;
    border: 1px solid #555555; 
    border-radius: 4px;
    padding: 5px;
}

QPushButton {
    background-color: #27ae60; 
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-size: 14px;
}

QPushButton:hover {
    background-color: #2ecc71; 
}

QPushButton:pressed {
    background-color: #27ae60; 
}

QProgressBar {
    background-color: rgba(250, 250, 250, 10);
    border: none;
    border-radius: 0px;
}

QProgressBar::chunk {
    background-color: #2ecc71;
}
"""

# Стили для поиска
SEARCH_STYLES = """
QLineEdit {
    background-color: #2D2D2D;
    border: 1px solid #404040;
    border-radius: 5px;
    padding: 3px 12px;
    color: #FFFFFF;
    font-size: 13px;
    min-width: 250px;
}

QLineEdit:focus {
    border: 1px solid #5E5E5E;
    background-color: #2D2D2D;
}
"""

# Стили для заметок
NOTES_STYLES = """
QTextEdit {
    background-color: #2d2d2d;
    border: 1px solid #3D3D3D;
    border-radius: 5px;
    padding: 5px;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 14px;
    color: #FFFFFF;
}
"""

# Стили для статуса пароля
PASSWORD_STATUS_STYLES = """
QLabel {
    padding: 2px 6px;
    border-radius: 2px;
    font-size: 11px;
}
"""

# Стили для окна аутентификации
AUTH_STYLES = """
QWidget {
    background-color: transparent;
}

QLabel {
    color: #ffffff;
    font-size: 20px;
    font-weight: bold;
}

QLineEdit {
    background-color: #1C1C1E;
    color: #ffffff;
    border: 1px solid #3D3D3D;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 13px;
    min-height: 20px;
}

QLineEdit:focus {
    border: 1px solid #606060;
}

QToolButton {
    background-color: transparent;
    border: none;
    padding: 0px;
}

QLabel#messageLabel {
    color: #ff3b30;
    font-size: 12px;
    margin-top: 4px;
}

QLabel#titleLabel {
    font-size: 18px;
    font-weight: bold;
    color: #ecf0f1;
}

"""

# Стили для групп настроек и секций
SETTINGS_GROUPBOX_STYLES = """
QGroupBox {
    color: #ffffff;
    border-radius: 8px;
    margin-top: 10px;
    font-size: 15px;
}
QGroupBox::title {
    color: #ffffff;
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px 0 5px;
    background-color: transparent;
    font-size: 15px;
    font-weight: bold;
}
QLabel {
    color: #ffffff;
}
QRadioButton {
    color: #ffffff;
    font-size: 14px;
}
QRadioButton:disabled {
    color: #888888;
}
QSpinBox {
    background-color: #222;
    color: #ffffff;
    border: 1px solid #444;
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 14px;
}
QSpinBox::up-button, QSpinBox::down-button {
    background-color: #333;
    border: none;
    border-radius: 2px;
    margin: 2px;
}
QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background-color: #505050;
}
"""

# Стили для формы
FORM_STYLES = """
QGroupBox {
    background-color: transparent;
    border-radius: 0px;
}

QLabel {
    color: #ffffff;
    font-size: 14px;
}

QLabel[required="true"] {
    color: #ffffff;
}

QLabel[required="true"]::after {
    content: " *";
    color: #ffffff;
}
"""