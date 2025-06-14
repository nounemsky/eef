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
from styles.themes import THEMES


class TagsContainer(QWidget):
    tag_clicked = pyqtSignal(dict)

    def __init__(self, parent=None, theme="default"):
        super().__init__(parent)
        print("TagsContainer initialized")
        self.setObjectName("TagsContainer")
        self.theme = theme
        self.selected_chip = None
        
        # Создаем QScrollArea
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setObjectName("TagsScrollArea")
        
        # Создаем внутренний контейнер
        self.container = QWidget()
        self.container.setObjectName("TagsInnerContainer")
        
        # Создаем layout для внутреннего контейнера
        self.flow_layout = VerticalFlowLayout(self.container, spacing=10, column_count=1)
        self.container.setLayout(self.flow_layout)
        
        # Устанавливаем внутренний контейнер в QScrollArea
        self.scroll.setWidget(self.container)
        
        # Создаем основной layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 0, 5, 0)
        main_layout.addWidget(self.scroll)
        
        # Устанавливаем политику размера
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Применяем стили
        self.update_theme(theme)

    def update_theme(self, theme):
        """Обновляет тему контейнера"""
        self.theme = theme
        theme_styles = THEMES[theme]["TAGS_CONTAINER_STYLES"]
        
        # Применяем стили к основному контейнеру
        self.setStyleSheet(theme_styles)
        
        # Обновляем стили всех чипов
        for i in range(self.flow_layout.count()):
            item = self.flow_layout.itemAt(i)
            if item and item.widget():
                chip = item.widget()
                if hasattr(chip, 'update_theme'):
                    chip.update_theme(theme)

    def add_tag(self, entry_data):
        """Добавляет тег в контейнер"""
        print(f"Adding tag for {entry_data.get('service', 'unknown')}")
        chip = ChipWidget(entry_data, theme=self.theme)
        chip.clicked.connect(lambda data=entry_data: self._on_chip_clicked(data))
        self.flow_layout.addWidget(chip)
        
    def _on_chip_clicked(self, data):
        """Обработчик клика по чипу"""
        print(f"Chip clicked: {data.get('service', 'unknown')}")
        
        # Находим чип, по которому кликнули
        clicked_chip = None
        for i in range(self.flow_layout.count()):
            chip = self.flow_layout.itemAt(i).widget()
            if chip.entry_data == data:
                clicked_chip = chip
                break
        
        # Если нашли чип
        if clicked_chip:
            # Если был ранее выбранный чип, снимаем с него выделение
            if self.selected_chip and self.selected_chip != clicked_chip:
                self.selected_chip.set_selected(False)
            
            # Обновляем выбранный чип
            self.selected_chip = clicked_chip
        
        self.tag_clicked.emit(data)

    def clear(self):
        """Очищает все теги из контейнера"""
        self.selected_chip = None
        while self.flow_layout.count():
            item = self.flow_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.flow_layout.update()


class ChipWidget(QWidget):
    clicked = pyqtSignal(dict)

    def __init__(self, entry_data, theme="default", parent=None):
        super().__init__(parent)
        self.entry_data = entry_data
        print(f"ChipWidget initialized for {entry_data.get('service', 'unknown')}")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("ChipWidget")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.theme = theme
        self.is_selected = False
        self.setProperty("selected", False)
        
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
        login_label.setObjectName("loginLabel")

        # URL или сервис как вторичный текст
        secondary_text = entry_data.get('url', '') or entry_data.get('service', '')
        if secondary_text:
            secondary_label = QLabel(extract_domain(secondary_text))
            secondary_label.setObjectName("secondaryLabel")
            info_layout.addWidget(secondary_label)

        info_layout.addWidget(login_label)
        content_layout.addWidget(self.icon_label)
        content_layout.addWidget(info_container)
        layout.addWidget(content_container)

        # Применяем стили
        self.update_theme(theme)

    def update_theme(self, theme):
        """Обновляет тему чипа"""
        self.theme = theme
        theme_styles = THEMES[theme]
        
        # Применяем стили к чипу
        chip_styles = theme_styles["CHIP_WIDGET_STYLES"]
        if isinstance(chip_styles, dict):
            chip_styles = chip_styles.get(theme, chip_styles.get("default", ""))
        self.setStyleSheet(chip_styles)
        
        # Обновляем стили меток
        label_styles = theme_styles["CHIP_LABEL_STYLES"]
        if isinstance(label_styles, dict):
            login_style = label_styles.get("login", "")
            secondary_style = label_styles.get("secondary", "")
        else:
            login_style = ""
            secondary_style = ""
            
        for label in self.findChildren(QLabel):
            if label.objectName() == "loginLabel":
                label.setStyleSheet(login_style)
            elif label.objectName() == "secondaryLabel":
                label.setStyleSheet(secondary_style)

    def _create_strength_indicator(self, password):
        """Создает индикатор надежности пароля"""
        indicator = QWidget()
        indicator.setFixedWidth(4)
        strength = password_strength(password)
        color = THEMES[self.theme]["PASSWORD_STRENGTH_COLORS"][strength]
        
        def paintEvent(e):
            painter = QPainter(indicator)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            brush = QBrush(QColor(color))
            painter.fillRect(indicator.rect(), brush)
            
        indicator.paintEvent = paintEvent
        return indicator

    def mousePressEvent(self, event):
        """Обработчик нажатия мыши"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_selected = not self.is_selected
            self.setProperty("selected", self.is_selected)
            self.style().unpolish(self)
            self.style().polish(self)
            self.clicked.emit(self.entry_data)

    def set_selected(self, selected):
        """Устанавливает состояние выбора чипа"""
        if self.is_selected != selected:
            self.is_selected = selected
            self.setProperty("selected", selected)
            self.style().unpolish(self)
            self.style().polish(self)

class PasswordWidget(QWidget):
    def __init__(self, entry_data, parent=None):
        super().__init__(parent)
        
        # Создаем метку для логина
        login_label = QLabel(entry_data.get('login', ''))
        login_label.setProperty('class', 'loginLabel')
        
        # Создаем метку для дополнительной информации
        secondary_info = entry_data.get('email', '') or entry_data.get('phone', '')
        if secondary_info:
            secondary_label = QLabel(secondary_info)
            secondary_label.setProperty('class', 'secondaryLabel') 