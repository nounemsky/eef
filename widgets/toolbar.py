from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QMouseEvent


class ToolbarWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.parent.drag_pos = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self.parent, 'drag_pos'):
            delta = event.globalPosition().toPoint() - self.parent.drag_pos
            self.parent.move(self.parent.pos() + delta)
            self.parent.drag_pos = event.globalPosition().toPoint()
            event.accept() 