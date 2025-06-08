from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor
from styles import CHIP_STYLES


class ChipWidget(QWidget):
    clicked = pyqtSignal(dict)

    def __init__(self, entry_data, favicon_path, styles=None, parent=None):
        super().__init__(parent)
        self.entry_data = entry_data
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("ChipWidget")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.styles = styles or {
            "background": "#141414",
            "border_top": "0px",
            "border_right": "0px",
            "border_bottom": "1px solid #444",
        }
        self.setStyleSheet(CHIP_STYLES['default'])

    def enterEvent(self, event):
        self.setStyleSheet(CHIP_STYLES['hover'])
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet(CHIP_STYLES['default'])
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.entry_data) 