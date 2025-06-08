from PyQt6.QtWidgets import QLayout, QLayoutItem, QSizePolicy
from PyQt6.QtCore import QSize, QRect


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