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
"""

# Стили для списка паролей
PASSWORD_LIST_STYLES = """
#passwordList {
    alternate-background-color: transparent;
}
"""

TAGS_CONTAINER_STYLES = """
#TagsContainer {
    background-color: #1a0033;
    border-radius: 4px;
    padding: 8px;
}

#TagsInnerContainer {
    background-color: #0f0026;
    border-radius: 0px;
    padding: 5px;
}

QScrollArea#TagsScrollArea {
    background-color: transparent;
    border: none;
}

QWidget#TagsScrollViewport {
    background-color: transparent;
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
    border-top: 1px solid #444;
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
    'base': """
        QLabel {
            color: white;
            padding: 10px 16px;
            border-radius: 6px;
            font-size: 12px;
        }
    """,
    
    'default': """
        QLabel {
            background-color: #1e1e1e;
            border: 1px solid #404040;
        }
    """,
    
    'error': """
        QLabel {
            background-color: #cc3333;
        }
    """,
    
    'warning': """
        QLabel {
            background-color: #cc9933;
        }
    """,
    
    'success': """
        QLabel {
            background-color: #33cc33;
        }
    """
} 