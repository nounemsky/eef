"""Стили компонентов приложения"""

# Стили для кнопок управления окном
WINDOW_CONTROL_STYLES = """
#closeButton, #minimizeButton, #maximizeButton {
    border: none;
    border-radius: 8px;
    width: 16px;
    height: 16px;
}

#closeButton {
    background-color: #ff5f57;
}

#closeButton:hover {
    background-color: #ff3b30;
}

#minimizeButton {
    background-color: #febc2e;
}

#minimizeButton:hover {
    background-color: #fea500;
}

#maximizeButton {
    background-color: #28c940;
}

#maximizeButton:hover {
    background-color: #1d9d30;
}

QPushButton.windowButton {
    background-color: transparent;
    color: white;
    border-left: 1px solid #444;
    font-size: 20px;
    font-weight: bold;
    padding: 0px;
    text-align: center;
}

QPushButton.windowButton:hover {
    background-color: rgba(255, 255, 255, 0.15);
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

# Стили для списка паролей
PASSWORD_LIST_STYLES = """
#passwordList {
    alternate-background-color: transparent;
}
"""

# Стили для контейнера тегов
TAGS_CONTAINER_STYLES = """
QWidget#TagsContainer {
    background-color: #141414;
    border: 1px solid #333;
    border-radius: 4px;
    padding: 8px;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

QWidget#TagsInnerContainer {
    background-color: #1a1a1a;
    border-radius: 0px;
    padding: 5px;
}

QLabel.loginLabel {
    color: #ffffff;
    font-size: 14px;
    font-weight: bold;
}

QLabel.secondaryLabel {
    color: #808080;
    font-size: 12px;
}
"""

# Стили для панелей
PANEL_STYLES = """
#LeftPanel {
    border-right: 1px solid #444;
    border-top: 1px solid #444;
    background-color: transparent;
}

#RightPanel {
    border-left: 1px solid #444;
    border-top: 1px solid #ffffff;
    background-color: transparent;
}

QSplitter::handle {
    background: #444;
    width: 1px;
    height: 1px;
}

QSplitter::handle:hover {
    background: #FFFFFF;
}

QSplitter::handle:pressed {
    background: #FFFFFF;
}
"""

# Стили для оверлея сообщений
OVERLAY_MESSAGE_STYLES = {
    "default": {
        "base": """
            QLabel {
                background-color: rgba(33, 33, 33, 0.9);
                color: white;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
            }
        """,
        "default": """
            background-color: rgba(33, 33, 33, 0.9);
            color: white;
        """,
        "error": """
            background-color: rgba(183, 28, 28, 0.9);
            color: white;
        """,
        "warning": """
            background-color: rgba(245, 124, 0, 0.9);
            color: white;
        """,
        "success": """
            background-color: rgba(46, 125, 50, 0.9);
            color: white;
        """
    },
    "cyberpunk": {
        "base": """
            QLabel {
                background-color: rgba(15, 0, 38, 0.95);
                color: #00fff7;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
                border: 1px solid #ff00ea;
                text-shadow: 0 0 10px #00fff7;
            }
        """,
        "default": """
            background-color: rgba(15, 0, 38, 0.95);
            color: #00fff7;
            border: 1px solid #ff00ea;
            text-shadow: 0 0 10px #00fff7;
        """,
        "error": """
            background-color: rgba(15, 0, 38, 0.95);
            color: #ff0000;
            border: 1px solid #ff0000;
            text-shadow: 0 0 10px #ff0000;
        """,
        "warning": """
            background-color: rgba(15, 0, 38, 0.95);
            color: #ffae00;
            border: 1px solid #ffae00;
            text-shadow: 0 0 10px #ffae00;
        """,
        "success": """
            background-color: rgba(15, 0, 38, 0.95);
            color: #00ff66;
            border: 1px solid #00ff66;
            text-shadow: 0 0 10px #00ff66;
        """
    }
} 