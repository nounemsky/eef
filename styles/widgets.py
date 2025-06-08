"""Стили виджетов приложения"""

# Стили для чипа (ChipWidget)
CHIP_STYLES = {
      'default': """
          QWidget#ChipWidget {
              background-color: rgba(0,0,0,0.2);
            border-top: 0px;
            border-right: 0px;
            border-bottom: 1px solid #444;
            padding: 10px;
        }
    """,
    'hover': """
        QWidget#ChipWidget {
            background-color: #1a1a1a;
            border-top: 0px;
            border-right: 0px;
            border-bottom: 1px solid #444;
            padding: 10px;
        }
    """
}

# Стили для ленивой иконки (LazyIconLabel)
LAZY_ICON_STYLES = """
    QLabel {
        background-color: transparent;
        border: none;
    }
"""

# Стили для статуса пароля (PasswordStatusWidget)
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
            background-color: #4CAF5015;
            border: 1px solid #4CAF5030;
            color: #4CAF50;
        }
    """,
    'warning': """
        QLabel {
            background-color: #FFA72615;
            border: 1px solid #FFA72630;
            color: #FFA726;
        }
    """,
    'danger': """
        QLabel {
            background-color: #F4433615;
            border: 1px solid #F4433630;
            color: #F44336;
        }
    """
}

# Стили для кнопки пропуска (SkipButton)
SKIP_BUTTON_STYLES = """
    QPushButton {
        background-color: transparent;
        color: #707070;
        border: none;
        padding: 4px 8px;
        font-size: 14px;
        text-decoration: underline;
        transition: color 0.2s;
    }
    QPushButton:hover {
        color: #ffffff;
    }
    QPushButton:pressed {
        color: #ffffff;
    }
"""

# Стили для кнопки добавления (AddButton)
ADD_BUTTON_STYLES = """
    QPushButton {
        background-color: #1DB954;
        color: white;
        border: none;
        border-radius: 10px;
        font-size: 24px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #1ed760;
    }
    QPushButton:pressed {
        background-color: #1aa34a;
    }
""" 