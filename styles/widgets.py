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

# Стили для кнопки пропуска
SKIP_BUTTON_STYLES = """
    QPushButton {
        background-color: transparent;
        color: #707070;
        border: none;
        padding: 4px 8px;
        font-size: 14px;
        text-decoration: underline;
    }
    QPushButton:hover {
        color: #ffffff;
    }
    QPushButton:pressed {
        color: #ffffff;
    }
"""

# Стили для кнопки добавления
ADD_BUTTON_STYLES = """
    QPushButton {
        background-color: #1DB954;
        color: white;
        border: none;
        border-radius: 10px;
        font-size: 12px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #1ed760;
    }
    QPushButton:pressed {
        background-color: #1aa34a;
    }
"""

# Стили для кнопки Continue
CONTINUE_BUTTON_STYLES = """
    QPushButton {
        background-color: #ffffff;
        color: #000000;
        border: 2px solid #202020;
        border-radius: 20px;
        min-width: 235px;
        min-height: 40px;
        text-align: center;
        font-size: 14px;
        font-weight: bold;
        padding: 0;
        margin: 0;
    }
    QPushButton:hover {
        background-color: #f0f0f0;
        border: 1px solid #000000;
        border-radius: 5px;
    }
    QPushButton:pressed {
        background-color: #e0e0e0;
        border: 1px solid #000000;
        border-radius: 5px;
    }
"""

# Стили для чипов
CHIP_WIDGET_STYLES = {
    "default": """
        QWidget#ChipWidget {
            background: #404040;
            border: 1px solid #333333;
            border-radius: 4px;
            padding: 50px;
        }
        QWidget#ChipWidget:hover {
            background: #2A2A2A;
            border: 1px solid #444444;
        }
        QWidget#ChipWidget[selected="true"] {
            background: #2A2A2A;
            border: 1px solid #444444;
        }
        QWidget#ChipWidget QLabel {
            color: #FFFFFF;
            font-size: 14px;
        }
        QWidget#ChipWidget QLabel[secondaryLabel="true"] {
            color: #888888;
            font-size: 12px;
        }
    """,

    "cyberpunk": """
        QWidget#ChipWidget {
            background-color: transparent;
            background-image: url("styles/images/cyberpunk/CHIP.png");
            background-repeat: no-repeat;
            background-position: right center;
            border: none;
            border-radius: 0px;
            padding: 8px;
        }
        QWidget#ChipWidget:hover {
            background-image: url("styles/images/cyberpunk/CHIPHOVER.png");

        }
        QWidget#ChipWidget[selected="true"] {
            background-image: url("styles/images/cyberpunk/CHIPPRESSED.png");
        }
        QWidget#ChipWidget QLabel {
            color: #FFFFFF;
            font-size: 14px;
        }
        QWidget#ChipWidget QLabel[secondaryLabel="true"] {
            color: #FFFFFF;
            font-size: 12px;
        }
    """
}

# Стили для контейнера тегов
TAGS_CONTAINER_STYLES = {
    "default": {
        "container": """
            QWidget#TagsContainer {
                background: transparent;
                border: none;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QWidget#TagsInnerContainer {
                background-color: #141414;
                border-radius: 0px;
                padding: 5px;
            }
        """
    },
    "cyberpunk": {
        "container": """
            QWidget#TagsContainer {
                background: transparent;
                border: none;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QWidget#TagsInnerContainer {
                background-color: #0f0026;
                border-radius: 0px;
                padding: 5px;
                border: 1px solid #ff00ea;
            }
        """
    }
}

# Стили для индикатора надежности пароля
PASSWORD_STRENGTH_COLORS = {
    "default": {
        0: "rgba(229, 57, 53, 0.8)",      # Красный
        1: "rgba(251, 140, 0, 0.8)",      # Оранжевый
        2: "rgba(251, 192, 45, 0.8)",     # Желтый
        3: "rgba(67, 160, 71, 0.8)",      # Зеленый
        4: "rgba(46, 125, 50, 0.8)"       # Темно-зеленый
    },
    "cyberpunk": {
        0: "rgba(255, 0, 0, 0.8)",        # Неоновый красный
        1: "rgba(255, 165, 0, 0.8)",      # Неоновый оранжевый
        2: "rgba(255, 255, 0, 0.8)",      # Неоновый желтый
        3: "rgba(0, 255, 247, 0.8)",      # Неоновый голубой
        4: "rgba(255, 0, 234, 0.8)"       # Неоновый розовый
    }
}

# Стили для меток в чипах
CHIP_LABEL_STYLES = {
    "default": {
        "login": """
            color: #FFFFFF;
            font-size: 14px;
            font-weight: bold;
        """,
        "secondary": """
            color: #888888;
            font-size: 12px;
        """
    },
    "cyberpunk": {
        "login": """
            color: #FFFFFF;
            font-size: 14px;
            font-family: 'Orbitron';
            font-weight: bold;
        """,
        "secondary": """
            color: #00fff7;
            font-family: 'Rajdhani Regular';
            font-size: 14px;
        """
    }
}

THEME_COMBOBOX_STYLES = {
    "default": """
        QComboBox {
            background-color: #2D2D2D;
            color: white;
            border: 1px solid #404040;
            border-radius: 4px;
            padding: 5px;
            min-height: 25px;
        }
        QComboBox:hover {
            background-color: #383838;
            border-color: #505050;
        }
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        QComboBox::down-arrow {
            width: 12px;
            height: 12px;
        }
        QComboBox QAbstractItemView {
            background-color: #2D2D2D;
            color: white;
            selection-background-color: #404040;
            selection-color: white;
            border: 1px solid #505050;
        }
    """,
    "cyberpunk": """
        QComboBox {
            background-color: rgba(15, 0, 38, 0.95);
            color: #00fff7;
            border: 1px solid #ff00ea;
            border-radius: 4px;
            padding: 5px;
            min-height: 25px;
            font-weight: bold;
        }
        QComboBox:hover {
            background-color: rgba(15, 0, 38, 0.8);
            border-color: #00fff7;
        }
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        QComboBox::down-arrow {
            width: 12px;
            height: 12px;
        }
        QComboBox QAbstractItemView {
            background-color: rgba(15, 0, 38, 0.95);
            color: #00fff7;
            selection-background-color: rgba(0, 255, 247, 0.15);
            selection-color: #00fff7;
            border: 1px solid #ff00ea;
        }
    """
} 