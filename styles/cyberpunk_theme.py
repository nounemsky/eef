APP_STYLES = """
#MainContainer {
    background-color: #0f0026;
    border-radius: 8px;
    border: 1px solid #00fff7;
    box-shadow: 0px 0px 20px #00fff7;
}
#CentralWidget {
    background-color: #1a0033;
    border-top: 1px solid #00fff7;
    border-radius: 0px;
}
QLabel { color: #00fff7; font-size: 16px; }
QLineEdit {
    background-color: #1a0033;
    color: #ff00ea;
    border: 1px solid #00fff7;
    border-radius: 4px;
    padding: 5px;
}
QListWidget, QComboBox {
    background-color: #1a0033;
    color: #00fff7;
    border: 1px solid #00fff7;
    border-radius: 4px;
    padding: 5px;
}
QPushButton {
    background-color: #ff00ea;
    color: #0f0026;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-size: 14px;
    font-weight: bold;
    box-shadow: 0px 0px 10px #00fff7;
}
QPushButton:hover {
    background-color: #00fff7;
    color: #ff00ea;
}
QPushButton:pressed {
    background-color: #ff00ea;
    color: #0f0026;
}
QProgressBar {
    background-color: #1a0033;
    border: none;
    border-radius: 0px;
}
QProgressBar::chunk {
    background-color: #ff00ea;
}
"""

SEARCH_STYLES = """
QLineEdit {
    background-color: rgba(0, 0, 0, 172);
    border: 1px solid #00F0FF;
    border-radius: 0px;
    padding: 3px 12px;
    color: #cdcdcd;
    font-size: 14px;
    min-width: 250px;
}
QLineEdit:focus {
    border: 1px solid #ff00ea;
    background-color: #1a0033;
}
"""

NOTES_STYLES = """
QTextEdit {
    background-color: #1a0033;
    border: 1px solid #00fff7;
    border-radius: 5px;
    padding: 5px;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 14px;
    color: #ff00ea;
}
"""

PANEL_STYLES = """
#LeftPanel {
    border-right: 1px solid #00fff7;
    border-top: 1px solid #00fff7;
    background-color: #0f0026;
}
#RightPanel {
    border-left: 1px solid #00fff7;
    border-top: 1px solid #00fff7;
    background-color: #0f0026;
}
#CenterPanel {
    background-color: #1a0033;
}
QSplitter::handle {
    background: #ff00ea;
    width: 1px;
    height: 1px;
}
QSplitter::handle:hover {
    background: #00fff7;
}
QSplitter::handle:pressed {
    background: #ff00ea;
}
"""

TAGS_CONTAINER_STYLES = """
#TagsContainer {
    background-color: #00ff00;
}
QScrollArea#TagsScrollArea {
    background-color: #00ff00;
    border: none;
}
QWidget#TagsScrollViewport {
    background-color: #00ff00;
}
#TagsInnerContainer {
    background-color: #00ff00;
    border-radius: 0px;
    padding: 5px;
}
#CenterPanel {
    background-color: #00ff00;
}
"""

PASSWORD_LIST_STYLES = """
#passwordList {
    alternate-background-color: #1a0033;
}
"""

WINDOW_CONTROL_STYLES = """
#closeButton, #minimizeButton, #maximizeButton {
    border: none;
    border-radius: 8px;
    width: 16px;
    height: 16px;
}
#closeButton {
    background-color: #ff0055;
}
#closeButton:hover {
    background-color: #ff00ea;
}
#minimizeButton {
    background-color: #00fff7;
}
#minimizeButton:hover {
    background-color: #00bfff;
}
#maximizeButton {
    background-color: #ff00ea;
}
#maximizeButton:hover {
    background-color: #ff0055;
}
"""

OVERLAY_MESSAGE_STYLES = {
    'base': """
        QLabel {
            color: #00fff7;
            padding: 10px 16px;
            border-radius: 6px;
            font-size: 12px;
        }
    """,
    'default': """
        QLabel {
            background-color: #1a0033;
            border: 1px solid #00fff7;
        }
    """,
    'error': """
        QLabel {
            background-color: #ff0055;
        }
    """,
    'warning': """
        QLabel {
            background-color: #ff00ea;
        }
    """,
    'success': """
        QLabel {
            background-color: #00fff7;
        }
    """
}

CHIP_STYLES = {
    'default': """
        QWidget#ChipWidget {
            background-color: #0f0026;
            border-top: 0px;
            border-right: 0px;
            border-bottom: 1px solid #00fff7;
            padding: 10px;
        }
    """,
    'hover': """
        QWidget#ChipWidget {
            background-color: #1a0033;
            border-top: 0px;
            border-right: 0px;
            border-bottom: 1px solid #ff00ea;
            padding: 10px;
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
        color: #00fff7;
        border: none;
        padding: 4px 8px;
        font-size: 14px;
        text-decoration: underline;
        transition: color 0.2s;
    }
    QPushButton:hover {
        color: #ff00ea;
    }
    QPushButton:pressed {
        color: #ff0055;
    }
"""

ADD_BUTTON_STYLES = """
    QPushButton {
        background-color: #ff00ea;
        color: #0f0026;
        border: none;
        border-radius: 10px;
        font-size: 24px;
        font-weight: bold;
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