from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QSizePolicy
)
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QIcon
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from .base_widgets import VerticalFlowLayout
from .lazy_icon import LazyIconLabel
from utils.url_utils import extract_domain
from utils.password_utils import password_strength
import os


class TagsContainer(QWidget):
    tag_clicked = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        print("TagsContainer initialized")  # Отладка
        self.setObjectName("TagsContainer")
        self.scroll = QScrollArea()
        self.scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)
        self.scroll.setWidgetResizable(True)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.container = QWidget()
        self.flow_layout = VerticalFlowLayout(self.container, spacing=10, column_count=1)
        self.container.setLayout(self.flow_layout)

        self.container.setObjectName("TagsInnerContainer")
        self.container.setStyleSheet("""
            QWidget#TagsInnerContainer {
                background-color: #141414;
                border-radius: 0px;
                padding: 5px;
            }
        """)

        self.scroll.setWidget(self.container)
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.scroll)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def add_tag(self, entry_data):
        """Добавляет тег в контейнер"""
        print(f"Adding tag for {entry_data.get('service', 'unknown')}")  # Отладка
        chip = ChipWidget(entry_data)
        chip.clicked.connect(lambda data=entry_data: self._on_chip_clicked(data))
        self.flow_layout.addWidget(chip)
        
    def _on_chip_clicked(self, data):
        """Обработчик клика по чипу"""
        print(f"Chip clicked: {data.get('service', 'unknown')}")  # Отладка
        self.tag_clicked.emit(data)

    def clear(self):
        """Очищает все теги из контейнера"""
        while self.flow_layout.count():
            item = self.flow_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.flow_layout.update()


class ChipWidget(QWidget):
    clicked = pyqtSignal(dict)

    def __init__(self, entry_data, styles=None, parent=None):
        super().__init__(parent)
        self.entry_data = entry_data
        print(f"ChipWidget initialized for {entry_data.get('service', 'unknown')}")  # Отладка
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("ChipWidget")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.styles = styles or {
            "background": "#1E1E1E",
            "hover_background": "#2A2A2A",
            "border": "1px solid #333333",
            "hover_border": "1px solid #444444",
            "text_color": "#FFFFFF",
            "secondary_text_color": "#888888",
            "radius": "4px",
            "padding": "8px"
        }

        self.hovered = False

        # Основной layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Индикатор надежности (вертикальная полоса слева)
        strength_indicator = self._create_strength_indicator(entry_data.get('password', ''))
        layout.addWidget(strength_indicator)

        # Контейнер для контента
        content_container = QWidget()
        content_layout = QHBoxLayout(content_container)
        content_layout.setContentsMargins(12, 8, 12, 8)
        content_layout.setSpacing(12)

        # Иконка с ленивой загрузкой
        self.icon_label = LazyIconLabel(os.path.join(os.path.dirname(os.path.dirname(__file__)), "app_cache", "favicons"))
        self.icon_label.set_url(entry_data.get('url', ''), entry_data.get('service', ''))

        # Информационный контейнер
        info_container = QWidget()
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(2)

        # Логин как основной текст
        login = entry_data.get('login', '')
        login_label = QLabel(login)
        login_label.setStyleSheet(f"""
            color: {self.styles['text_color']};
            font-size: 14px;
            font-weight: bold;
        """)

        # Сервис и URL как дополнительная информация
        secondary_info = []
        if service := entry_data.get('service', ''):
            secondary_info.append(service)
        if url := extract_domain(entry_data.get('url', '')):
            secondary_info.append(url)
        
        if secondary_info:
            secondary_label = QLabel(" • ".join(secondary_info))
            secondary_label.setStyleSheet(f"""
                color: {self.styles['secondary_text_color']};
                font-size: 12px;
            """)
            info_layout.addWidget(secondary_label)

        info_layout.addWidget(login_label)
        info_layout.addStretch()

        # Собираем все вместе
        content_layout.addWidget(self.icon_label)
        content_layout.addWidget(info_container, stretch=1)
        layout.addWidget(content_container)

        # Устанавливаем фиксированную высоту для виджета
        self.setFixedHeight(52)

    def _create_strength_indicator(self, password):
        """Создает индикатор надежности пароля"""
        indicator = QWidget()
        indicator.setFixedWidth(2)
        
        # Оцениваем надежность пароля
        strength = password_strength(password)
        
        # Определяем цвет индикатора
        colors = {
            0: "rgba(229, 57, 53, 0.8)",      # Красный
            1: "rgba(251, 140, 0, 0.8)",      # Оранжевый
            2: "rgba(251, 192, 45, 0.8)",     # Желтый
            3: "rgba(67, 160, 71, 0.8)",      # Зеленый
            4: "rgba(46, 125, 50, 0.8)"       # Темно-зеленый
        }
        
        color = colors.get(strength, colors[0])
        
        indicator.setStyleSheet(f"""
            QWidget {{
                background-color: {color};
                border: none;
            }}
        """)
        
        return indicator

    def enterEvent(self, event):
        self.hovered = True
        self.update()

    def leaveEvent(self, event):
        self.hovered = False
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Определяем цвета в зависимости от состояния
        bg_color = QColor(self.styles['hover_background'] if self.hovered else self.styles['background'])
        border_color = QColor(self.styles['hover_border'] if self.hovered else self.styles['border'])
        
        # Рисуем фон
        rect = self.rect()
        painter.setPen(QPen(border_color, 1))
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(rect.adjusted(0, 0, -1, -1), 6, 6)

    def mousePressEvent(self, event):
        print(f"ChipWidget clicked: {self.entry_data.get('service', 'unknown')}")  # Отладка
        self.clicked.emit(self.entry_data) 