from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette
from widgets.vertical_flow_layout import VerticalFlowLayout


class TagsContainer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TagsContainer")
        self.scroll = QScrollArea()
        self.scroll.setObjectName("TagsScrollArea")
        self.scroll.viewport().setObjectName("TagsScrollViewport")
        self.scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)
        # Принудительно делаем фон viewport прозрачным
        palette = self.scroll.viewport().palette()
        palette.setColor(self.scroll.viewport().backgroundRole(), Qt.GlobalColor.transparent)
        self.scroll.viewport().setPalette(palette)
        self.scroll.viewport().setAutoFillBackground(True)

        # Диагностика: выводим palette, stylesheet и objectName
        print('--- TAGS CONTAINER DEBUG ---')
        print('TagsContainer objectName:', self.objectName())
        print('TagsContainer styleSheet:', self.styleSheet())
        print('TagsContainer palette:', self.palette().color(self.backgroundRole()))
        print('ScrollArea objectName:', self.scroll.objectName())
        print('ScrollArea styleSheet:', self.scroll.styleSheet())
        print('ScrollArea palette:', self.scroll.palette().color(self.scroll.backgroundRole()))
        print('Viewport objectName:', self.scroll.viewport().objectName())
        print('Viewport styleSheet:', self.scroll.viewport().styleSheet())
        print('Viewport palette:', self.scroll.viewport().palette().color(self.scroll.viewport().backgroundRole()))
        print('---------------------------')

        self.container = QWidget()
        self.flow_layout = VerticalFlowLayout(self.container, spacing=10, column_count=1)
        self.container.setLayout(self.flow_layout)

        self.container.setObjectName("TagsInnerContainer")
        self.container.setStyleSheet("""
            #TagsInnerContainer {
                background-color: transparent;
                border-radius: 0px;
                padding: 5px;
    }
""")

        self.scroll.setWidget(self.container)
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.scroll)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def update_chip_styles(self, chip_style):
        """Обновляет стиль всех ChipWidget внутри контейнера"""
        for i in range(self.flow_layout.count()):
            item = self.flow_layout.itemAt(i)
            widget = item.widget()
            if widget:
                widget.setStyleSheet(chip_style) 