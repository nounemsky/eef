"""Стили диалогов приложения"""

# Стили для генератора паролей
PASSWORD_GENERATOR_STYLES = """
QDialog {
    background-color: #121212;
    border: 1px solid #3D3D3D;
    border-radius: 10px;
    color: white;
}

QLabel, QCheckBox {
    color: white;
    font-size: 13px;
}

QLineEdit {
    background-color: #1e1e1e;
    color: white;
    border: 1px solid #555;
    padding: 4px;
    border-radius: 4px;
}

QSpinBox {
    background-color: #1e1e1e;
    color: white;
    border: 1px solid #555;
    border-radius: 4px;
}

QPushButton {
    background-color: #333;
    color: white;
    padding: 5px 10px;
    border-radius: 4px;
}

QPushButton:hover {
    background-color: #444;
}
"""

# Стили для заголовка диалога
DIALOG_TITLE_BAR_STYLES = """
QWidget {
    background-color: #222;
}

QPushButton {
    background-color: #ff5f57;
    border: none;
    border-radius: 8px;
    width: 16px;
    height: 16px;
}

QPushButton:hover {
    color: red;
}
"""

# Стили для диалога настроек
SETTINGS_DIALOG_STYLES = """
QDialog {
    background-color: #141414;
}

QGroupBox {
    background-color: #1E1E1E;
    border: 1px solid #404040;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 10px;
}

QGroupBox::title {
    color: #FFFFFF;
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px 0 5px;
    background-color: #1E1E1E;
}

QPushButton {
    background-color: #27ae60;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    min-height: 32px;
    font-size: 14px;
}

QPushButton:hover {
    background-color: #2ecc71;
}

QPushButton:pressed {
    background-color: #219a52;
}
"""

# Стили для диалога подтверждения
CONFIRM_DIALOG_STYLES = """
QDialog {
    background-color: #141414;
    border: 1px solid #3D3D3D;
    border-radius: 8px;
}

QLabel {
    color: #FFFFFF;
    font-size: 14px;
}

QPushButton {
    background-color: #27ae60;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    min-height: 32px;
    font-size: 14px;
}

QPushButton:hover {
    background-color: #2ecc71;
}

QPushButton:pressed {
    background-color: #219a52;
}

QPushButton#cancelButton {
    background-color: #666666;
}

QPushButton#cancelButton:hover {
    background-color: #777777;
}
""" 