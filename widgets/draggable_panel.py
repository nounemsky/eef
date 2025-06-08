from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSplitter
from PyQt6.QtGui import QDrag, QPixmap
from PyQt6.QtCore import Qt, QMimeData


class DraggablePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.drag_start_position = None
        self.panel_layout = QVBoxLayout(self)
        self.panel_layout.setContentsMargins(5, 5, 5, 5)
        self.panel_layout.setSpacing(10)

    def add_content(self, widget):
        self.panel_layout.addWidget(widget)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.position().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return

        if not self.drag_start_position:
            return

        if (event.position().toPoint() - self.drag_start_position).manhattanLength() < 10:
            return

        mime_data = QMimeData()
        mime_data.setText(self.objectName())

        drag = QDrag(self)
        drag.setMimeData(mime_data)

        pixmap = QPixmap(self.size())
        self.render(pixmap)
        drag.setPixmap(pixmap)

        drag.exec(Qt.DropAction.MoveAction)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasText():
            source_panel = event.source()
            splitter = self.parent()

            if isinstance(splitter, QSplitter):
                index1 = splitter.indexOf(self)
                index2 = splitter.indexOf(source_panel)

                sizes = splitter.sizes()
                splitter.insertWidget(index1, source_panel)
                splitter.insertWidget(index2, self)
                splitter.setSizes(sizes)
                event.accept() 