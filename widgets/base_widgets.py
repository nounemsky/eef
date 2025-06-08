from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLayout,
    QLayoutItem, QSizePolicy, QSplitter
)
from PyQt6.QtGui import QMouseEvent, QPixmap, QDrag
from PyQt6.QtCore import Qt, QPoint, QMimeData, QRect, QSize


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


class DraggablePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.drag_start_position = None
        self.panel_layout = QVBoxLayout(self)
        self.panel_layout.setContentsMargins(5, 5, 5, 5)
        self.panel_layout.setSpacing(10)
        self._is_dragging = False

    def add_content(self, widget):
        self.panel_layout.addWidget(widget)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.position().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton) or self._is_dragging:
            return

        if not self.drag_start_position:
            return

        if (event.position().toPoint() - self.drag_start_position).manhattanLength() < 10:
            return

        self._is_dragging = True
        mime_data = QMimeData()
        mime_data.setText(self.objectName())

        drag = QDrag(self)
        drag.setMimeData(mime_data)

        pixmap = QPixmap(self.size())
        self.render(pixmap)
        drag.setPixmap(pixmap)

        drag.exec(Qt.DropAction.MoveAction)
        self._is_dragging = False

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

    def resizeEvent(self, event):
        """Обработчик изменения размера"""
        super().resizeEvent(event)
        # Обновляем максимальную ширину при изменении размера
        if event.size().width() > 0:
            self.setMaximumWidth(event.size().width())


class VerticalFlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=0, column_count=1):
        super().__init__(parent)
        self._items = []
        self.column_count = column_count
        self.spacing = spacing
        self.setContentsMargins(margin, margin, margin, margin)

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        return self._items[index] if 0 <= index < len(self._items) else None

    def takeAt(self, index):
        return self._items.pop(index) if 0 <= index < len(self._items) else None

    def sizeHint(self):
        return self._calculate_size()

    def minimumSize(self):
        return self._calculate_size()

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._arrange(rect)

    def _calculate_size(self):
        total_height = 0
        max_width = 0
        for item in self._items:
            size = item.sizeHint()
            total_height += size.height() + self.spacing
            max_width = max(max_width, size.width())
        return QSize(max_width * self.column_count, total_height)

    def _arrange(self, rect):
        column_width = (rect.width() - (self.column_count - 1) * self.spacing) // max(1, self.column_count)
        columns = [[] for _ in range(self.column_count)]
        column_heights = [0] * self.column_count

        for item in self._items:
            min_col = column_heights.index(min(column_heights))
            columns[min_col].append(item)
            column_heights[min_col] += item.sizeHint().height() + self.spacing

        for col_index, col in enumerate(columns):
            x = rect.x() + col_index * (column_width + self.spacing)
            y = rect.y()
            for item in col:
                item_geom = QRect(x, y, column_width, item.sizeHint().height())
                item.setGeometry(item_geom)
                y += item.sizeHint().height() + self.spacing