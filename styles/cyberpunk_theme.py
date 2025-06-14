"""Киберпанк тема для приложения"""

# Основные стили приложения
APP_STYLES = """
#MainContainer {
    background-color: transparent;
    background-image: url("styles/images/cyberpunk/background.png");
    background-repeat: no-repeat;
    background-position: center;
    border: 1px solid #000000;
}
#CentralWidget {
    background-color: transparent;
    border-top: 1px solid #F75049;
    border-radius: 0px;
}

QLabel {
    color: #00fff7;
    font-family: 'Rajdhani Regular';
    font-size: 14px;
}

QPushButton {
    background-color: #1a0040;
    color: #00fff7;
    border: 1px solid #ff00ea;
    border-radius: 4px;
    padding: 5px 10px;
    font-family: 'Rajdhani Regular';
}

QPushButton:hover {
    background-color: #2a0066;
    border: 1px solid #00fff7;
}

QPushButton:pressed {
    background-color: #3a008c;
}

QLineEdit {
    color: white;
    background-color: #001417;
    border-radius: 0px;
    border: 1px solid #02D7F2;
    padding: 3px 6px;
    font-size: 14px;
}
QLineEdit:hover {
    background-color: #002A30;
    border: 1px solid #02D7F2;
}

QLineEdit:focus {
    background-color: #001417;
    border: 1px solid #ffffff;
}
"""

# Стили для поиска
SEARCH_STYLES = """
QLineEdit {
    color: yellow;
    background-color: #001417;
    border-radius: 0px;
    border: 1px solid #02D7F2;
    padding: 3px 12px;
    font-size: 14px;
}

QLineEdit:hover {
    background-color: #002A30;
    border: 1px solid #02D7F2;
}

QLineEdit:focus {
    background-color: #001417;
    border: 1px solid #ffffff;
}
"""

# Стили для заметок
NOTES_STYLES = """
QTextEdit {
    background-color: #001417;
    border: 1px solid #00fff7;
    border-radius: 0px;
    padding: 5px;
    font-family: 'Rajdhani';
    font-size: 14px;
    color: white;
}
QTextEdit:hover {
    background-color: #002A30;
    border: 1px solid #02D7F2;
}

QTextEdit:focus {
    background-color: #001417;
    border: 1px solid #ffffff;
}
"""

# Стили для статуса пароля
PASSWORD_STATUS_STYLES = """
QLabel {
    padding: 2px 6px;
    border-radius: 2px;
    font-size: 11px;
    color: #00fff7;
    background-color: rgba(0, 255, 247, 0.1);
    border: 1px solid #00fff7;
}
"""

# Стили для аутентификации
AUTH_STYLES = """
QWidget {
    background-color: transparent;
}

QLabel {
    color: #00fff7;
    font-size: 20px;
    font-weight: bold;
}

QLineEdit {
    background-color: #001417;
    color: white;
    border: 1px solid #02D7F2;
    border-radius: 0px;
    padding: 6px 6px;
    font-family: 'Rajdhani Medium';
    font-size: 14px;
    min-height: 20px;
}

QLineEdit:hover {
    background-color: #002A30;
    border: 1px solid #02D7F2;
}

QLineEdit:focus {
    background-color: #001417;
    border: 1px solid #ffffff;
}

QToolButton {
    background-color: transparent;
    border: none;
    padding: 0px;
}

QLabel#messageLabel {
    color: #ff0055;
    font-size: 12px;
    margin-top: 4px;
    text-shadow: 0 0 10px #ff0055;
}

QLabel#titleLabel {
    font-family: 'Orbitron';
    font-size: 20px;
    font-weight: bold;
    color: #CDCDCD;
    color: #00fff7;
}

QPushButton#continue-btn {
    background-image: url("styles/images/cyberpunk/CONNECT.png");
    background-repeat: no-repeat;
    background-position: left center;
    border: none;
    border-radius: 0px;
    min-width: 250px;
    min-height: 40px;
    padding: 0px;
    margin: 0px;
    color: transparent;
}

QPushButton#continue-btn:hover {
    background-image: url("styles/images/cyberpunk/CONNECTHOVER.png");
    border: none;
}

QPushButton#continue-btn:pressed {
    background-image: url("styles/images/cyberpunk/CONNECTPRESSED.png");
    border: none;
}
"""

# Стили для групп настроек
SETTINGS_GROUPBOX_STYLES = """
QGroupBox {
    color: #00fff7;
    border-radius: 8px;
    margin-top: 10px;
    font-size: 15px;
    border: 1px solid #ff00ea;
}
QGroupBox::title {
    color: #00fff7;
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px 0 5px;
    background-color: #0f0026;
    font-size: 15px;
    font-weight: bold;
    text-shadow: 0 0 10px #00fff7;
}
QLabel {
    color: #02D7F2;
    text-shadow: 0 0 10px #00fff7;
}
QRadioButton {
    color: #00fff7;
    font-size: 14px;
    text-shadow: 0 0 10px #00fff7;
}
QRadioButton:disabled {
    color: #666666;
    text-shadow: none;
}
QSpinBox {
    background-color: #1a0040;
    color: #00fff7;
    border: 1px solid #ff00ea;
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 14px;
    text-shadow: 0 0 10px #00fff7;
}
QSpinBox::up-button, QSpinBox::down-button {
    background-color: #2a0066;
    border: none;
    border-radius: 2px;
    margin: 2px;
}
QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background-color: #3a008c;
}
"""

# Стили для контролов окна
WINDOW_CONTROL_STYLES = """
#closeButton, #minimizeButton, #maximizeButton {
    border: none;
    border-radius: 8px;
    width: 16px;
    height: 16px;
}

#closeButton {
    background-color: #2D0008;
    border: 1px solid #00F0FF;
}

#closeButton:hover {
    background-color: #000000;
    border: 1px solid #F75049;
}

#minimizeButton {
    background-color: #2D0008;
    border: 1px solid #00F0FF;
}

#minimizeButton:hover {
    background-color: #000000;
    border: 1px solid #F75049;
}

#maximizeButton {
    background-color: #2D0008;
    border: 1px solid #00F0FF;
}

#maximizeButton:hover {
    background-color: #000000;
    border: 1px solid #F75049;
}

QPushButton.windowButton {
    background-color: #ffffff;
    color: #00fff7;
    border-left: 1px solid #ff00ea;
    font-size: 20px;
    font-weight: bold;
    padding: 0px;
    text-align: center;
}

QPushButton.windowButton:hover {
    background-color: transparent;
}
"""

# Стили для списка паролей
PASSWORD_LIST_STYLES = """
QListWidget {
    background-color: #0f0026;
    border: 1px solid #ff00ea;
    border-radius: 4px;
}

QListWidget::item {
    color: #00fff7;
    padding: 5px;
    border-bottom: 1px solid #ff00ea;
}

QListWidget::item:selected {
    background-color: #2a0066;
    border: none;
}

QListWidget::item:hover {
    background-color: #1a0040;
}
"""

# Стили для панелей
PANEL_STYLES = """
QWidget#LeftPanel, QWidget#RightPanel {
    border: 1px solid #F75049;
    background-color: transperent;
}

QSplitter::handle {
    background: #F75049;
    width: 1px;
    height: 1px;
}

QSplitter::handle:hover {
    background: #00fff7;
}

QSplitter::handle:pressed {
    background: #00fff7;
}
"""

# Стили для контейнера тегов
TAGS_CONTAINER_STYLES = """
QWidget#TagsContainer {
    background-color: #0f0026;
    border: 1px solid #ff00ea;
    border-radius: 4px;
    padding: 8px;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

QWidget#TagsInnerContainer {
    background-color: transparent;
    border-radius: 0px;
    padding: 5px;
    border: 0p;
}
"""

OVERLAY_MESSAGE_STYLES = {
    'base': """
        QLabel {
            color: #00fff7;
            padding: 10px 16px;
            border-radius: 6px;
            font-size: 12px;
            text-shadow: 0 0 10px #00fff7;
            background-color: #1a0033;
            border: 1px solid #00fff7;
        }
    """,
    'default': """
        QLabel {
            color: #00fff7;
            padding: 10px 16px;
            border-radius: 6px;
            font-size: 12px;
            text-shadow: 0 0 10px #00fff7;
            background-color: #1a0033;
            border: 1px solid #00fff7;
        }
    """,
    'error': """
        QLabel {
            color: #0f0026;
            padding: 10px 16px;
            border-radius: 6px;
            font-size: 12px;
            text-shadow: 0 0 10px #ff0055;
            background-color: #ff0055;
            border: 1px solid #ff0055;
        }
    """,
    'warning': """
        QLabel {
            color: #0f0026;
            padding: 10px 16px;
            border-radius: 6px;
            font-size: 12px;
            text-shadow: 0 0 10px #ff00ea;
            background-color: #ff00ea;
            border: 1px solid #ff00ea;
        }
    """,
    'success': """
        QLabel {
            color: #0f0026;
            padding: 10px 16px;
            border-radius: 6px;
            font-size: 12px;
            text-shadow: 0 0 10px #00fff7;
            background-color: #00fff7;
            border: 1px solid #00fff7;
        }
    """
}

PASSWORD_STATUS_WIDGET_STYLES = {
    'base': """
        QLabel {
            padding: 2px 6px;
            border-radius: 2px;
            font-size: 11px;
        }
    """,
    'safe': """
        QLabel {
            background-color: #00fff715;
            border: 1px solid #00fff730;
            color: #00fff7;
        }
    """,
    'warning': """
        QLabel {
            background-color: #ff00ea15;
            border: 1px solid #ff00ea30;
            color: #ff00ea;
        }
    """,
    'danger': """
        QLabel {
            background-color: #ff005515;
            border: 1px solid #ff005530;
            color: #ff0055;
        }
    """
}

SKIP_BUTTON_STYLES = """
    QPushButton {
        background-color: transparent;
        color: #CDCDCD;
        border: none;
        padding: 4px 8px;
        font-size: 12px;
        text-decoration: underline;
    }
    QPushButton:hover {
        color: #CDCDCD;
    }
    QPushButton:pressed {
        color: #F75049;
    }
"""

ADD_BUTTON_STYLES = """
    QPushButton {
        background-color: transparent;
        background-image: url("styles/images/cyberpunk/ADD.png");
        background-repeat: no-repeat;
        background-position: right center;
        border: none;
        font-weight: bold;
        font-size: 14px;
        font-family: 'Regular';
        border-radius: 0px;
    }
    QPushButton:hover {
        background-image: url("styles/images/cyberpunk/ADDHOVER.png");
    }
    QPushButton:pressed {
        background-image: url("styles/images/cyberpunk/ADDPRESSED.png");
    }
"""

PASSWORD_GENERATOR_STYLES = """
QDialog {
    background-color: #0f0026;
    border: 1px solid #00fff7;
    border-radius: 10px;
    color: #ff00ea;
}
QLabel, QCheckBox {
    color: #00fff7;
    font-size: 13px;
}
QLineEdit {
    background-color: #1a0033;
    color: #ff00ea;
    border: 1px solid #00fff7;
    padding: 4px;
    border-radius: 4px;
}
QSpinBox {
    background-color: #1a0033;
    color: #ff00ea;
    border: 1px solid #00fff7;
    border-radius: 4px;
}
QPushButton {
    background-color: #ff00ea;
    color: #0f0026;
    padding: 5px 10px;
    border-radius: 4px;
}
QPushButton:hover {
    background-color: #00fff7;
    color: #ff00ea;
}
"""

DIALOG_TITLE_BAR_STYLES = """
QWidget {
    background-color: #1a0033;
}
QPushButton {
    background-color: #ff0055;
    border: none;
    border-radius: 8px;
    width: 16px;
    height: 16px;
}
QPushButton:hover {
    background-color: #ff00ea;
}
"""

SETTINGS_DIALOG_STYLES = """
QDialog {
    background-color: #0f0026;
}
QGroupBox {
    background-color: #1a0033;
    border: 1px solid #00fff7;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 10px;
}
QGroupBox::title {
    color: #ff00ea;
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px 0 5px;
    background-color: #1a0033;
}
QPushButton {
    background-color: #ff00ea;
    color: #0f0026;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    min-height: 32px;
    font-size: 14px;
}
QPushButton:hover {
    background-color: #00fff7;
    color: #ff00ea;
}
QPushButton:pressed {
    background-color: #ff0055;
    color: #00fff7;
}
"""

CONFIRM_DIALOG_STYLES = """
QDialog {
    background-color: #0f0026;
    border: 1px solid #00fff7;
    border-radius: 8px;
}
QLabel {
    color: #ff00ea;
    font-size: 14px;
}
QPushButton {
    background-color: #ff00ea;
    color: #0f0026;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    min-height: 32px;
    font-size: 14px;
}
QPushButton:hover {
    background-color: #00fff7;
    color: #ff00ea;
}
QPushButton:pressed {
    background-color: #ff0055;
    color: #00fff7;
}
QPushButton#cancelButton {
    background-color: #666666;
}
QPushButton#cancelButton:hover {
    background-color: #777777;
}
"""

WINDOW_BUTTON_STYLES = """
QPushButton.windowButton {
    background-color: transparent;
    color: #00fff7;
    border-left: 1px solid #00fff7;
    font-size: 20px;
    font-weight: bold;
    padding: 0px;
    text-align: center;
}

QPushButton.windowButton:hover {
    background-color: rgba(0, 255, 247, 0.15);
}

QLabel.loginLabel {
    color: #00fff7;
    font-size: 14px;
    font-weight: bold;
}

QLabel.secondaryLabel {
    color: #ff00ea;
    font-size: 12px;
}

QLabel#messageLabel {
    color: #ff0055;
    font-size: 12px;
    margin-top: 4px;
}

QLabel#titleLabel {
    font-size: 18px;
    font-weight: bold;
    color: #00fff7;
}

QToolButton {
    background-color: transparent;
    border: none;
    padding: 0px;
}

QToolButton:hover {
    background-color: rgba(0, 255, 247, 0.15);
}
"""

LAZY_ICON_STYLES = """
QLabel {
    background-color: transparent;
    border: none;
}
"""

# Стили для формы
FORM_STYLES = """
QGroupBox {
    background-color: transparent;
    border-radius: 0px;
}

QLabel {
    color: #FCEE09;
    font-family: 'Rajdhani Regular';
    font-size: 16px;
}

QLabel[required="true"] {
    color: #FCEE09;
    font-family: 'Rajdhani Regular';
    font-size: 16px;
}

QLabel[required="true"]::after {
    content: " *";
    color: #FCEE09;
    font-family: 'Rajdhani Regular';
    font-size: 16px;
}
"""