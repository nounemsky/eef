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
from styles.widgets import CHIP_LABEL_STYLES
import time
from datetime import datetime


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
        self.flow_layout = VerticalFlowLayout(self.container, spacing=3, column_count=1)
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
        try:
            super().__init__(parent)
            self.entry_data = entry_data
            self.theme = theme
            print(f"ChipWidget initialized for {entry_data.get('service', 'unknown')}")
            
            # Устанавливаем свойства
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            self.setObjectName("ChipWidget")
            self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
            self.is_selected = False
            self.setProperty("selected", False)
            
            # Создаем компоненты
            self._create_layouts()
            self._create_widgets()
            
            # Применяем стили в последнюю очередь
            self.update_theme(theme)
            
        except Exception as e:
            print(f"Ошибка инициализации ChipWidget: {str(e)}")
            raise
            
    def _create_layouts(self):
        """Создает все layout'ы"""
        try:
            # Основной layout
            self.main_layout = QHBoxLayout(self)
            self.main_layout.setContentsMargins(0, 0, 0, 0)
            self.main_layout.setSpacing(0)
            
            # Контейнер для контента
            self.content_container = QWidget()
            self.content_layout = QHBoxLayout(self.content_container)
            self.content_layout.setContentsMargins(0, 8, 12, 8) # ЧИП ВНУТРЕН
            self.content_layout.setSpacing(12)
            
            # Информационный контейнер
            self.info_container = QWidget()
            self.info_layout = QVBoxLayout(self.info_container)
            self.info_layout.setContentsMargins(0, 0, 0, 0)
            self.info_layout.setSpacing(2)
            
        except Exception as e:
            print(f"Ошибка создания layouts: {str(e)}")
            raise
            
    def _create_widgets(self):
        """Создает все виджеты"""
        try:
            # Индикатор надежности
            self.strength_indicator = self._create_strength_indicator(self.entry_data.get('password', ''))
            self.main_layout.addWidget(self.strength_indicator)
            
            # Иконка
            cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app_cache", "favicons")
            self.icon_label = LazyIconLabel(cache_dir, theme=self.theme)
            self.icon_label.set_url(self.entry_data.get('url', ''), self.entry_data.get('service', ''))
            
            # Логин
            login = self.entry_data.get('login', '')
            self.login_label = QLabel(login)
            self.login_label.setObjectName("loginLabel")
            
            # URL или сервис
            url = self.entry_data.get('url', '')
            service = self.entry_data.get('service', '')
            
            # Создаем отдельные метки для сервиса и URL
            if service:
                self.service_label = QLabel(service)
                self.service_label.setObjectName("serviceLabel")
                self.info_layout.addWidget(self.service_label)
            
            if url:
                url_text = extract_domain(url)
                if service:  # Если есть сервис, добавляем разделитель
                    url_text = f" • {url_text}"
                self.url_label = QLabel(url_text)
                self.url_label.setObjectName("urlLabel")
                
                # Если есть сервис, добавляем URL в тот же layout по горизонтали
                if service:
                    url_container = QWidget()
                    url_layout = QHBoxLayout(url_container)
                    url_layout.setContentsMargins(0, 0, 0, 0)
                    url_layout.setSpacing(0)
                    if hasattr(self, 'service_label'):
                        url_layout.addWidget(self.service_label)
                    url_layout.addWidget(self.url_label)
                    url_layout.addStretch()
                    self.info_layout.addWidget(url_container)
                else:
                    self.info_layout.addWidget(self.url_label)
            
            # Добавляем дату и время
            timestamp = self.entry_data.get('modified_at', self.entry_data.get('created_at'))
            if timestamp:
                dt = datetime.fromtimestamp(timestamp)
                date_str = dt.strftime("%d/%m/%Y")
                time_str = dt.strftime("%H:%M")
                
                # Создаем метки для даты и времени
                self.date_label = QLabel(date_str)
                self.time_label = QLabel(time_str)
                
                self.date_label.setObjectName("urlLabel")  # Используем тот же стиль, что и для URL
                self.time_label.setObjectName("urlLabel")  # Используем тот же стиль, что и для URL
                
                # Устанавливаем выравнивание и размер
                self.date_label.setAlignment(Qt.AlignmentFlag.AlignRight)
                self.time_label.setAlignment(Qt.AlignmentFlag.AlignRight)
                
                # Создаем контейнер для даты и времени
                datetime_container = QWidget()
                datetime_container.setObjectName("datetimeContainer")
                datetime_layout = QVBoxLayout(datetime_container)
                datetime_layout.setContentsMargins(0, 0, 0, 0)
                datetime_layout.setSpacing(0)
                datetime_layout.addWidget(self.time_label)
                datetime_layout.addWidget(self.date_label)
                
                # Устанавливаем трансформацию для поворота
                datetime_container.setStyleSheet("""
                    #datetimeContainer {
                        background: transparent;
                    }
                    #timeLabel {
                        color: #FF0000;
                        font-family: 'Rajdhani Medium';
                        font-size: 14px;
                    }
                    #dateLabel {
                        color: #FF0000;
                        font-family: 'Rajdhani Medium';
                        font-size: 14px;
                    }
                """)
            
            # Собираем все вместе
            self.info_layout.addWidget(self.login_label)
            
            # Создаем контейнер для даты справа
            right_container = QWidget()
            right_layout = QVBoxLayout(right_container)
            right_layout.setContentsMargins(0, 0, 0, 0)
            right_layout.setSpacing(0)
            right_layout.addStretch()
            if hasattr(self, 'date_label'):
                right_layout.addWidget(datetime_container)
            
            # Добавляем контейнеры в основной layout
            self.content_layout.addWidget(self.icon_label)
            self.content_layout.addWidget(self.info_container)
            self.content_layout.addWidget(right_container)
            self.main_layout.addWidget(self.content_container)
            
        except Exception as e:
            print(f"Ошибка создания widgets: {str(e)}")
            raise

    def _create_strength_indicator(self, password):
        """Создает индикатор надежности пароля"""
        try:
            indicator = QWidget()
            indicator.setFixedWidth(4)
            strength = min(max(password_strength(password), 0), 4)
            color = THEMES[self.theme]["PASSWORD_STRENGTH_COLORS"][strength]
            
            def paintEvent(e):
                try:
                    painter = QPainter(indicator)
                    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                    brush = QBrush(QColor(color))
                    painter.fillRect(indicator.rect(), brush)
                except Exception as pe:
                    print(f"Ошибка отрисовки индикатора: {str(pe)}")
                
            indicator.paintEvent = paintEvent
            return indicator
            
        except Exception as e:
            print(f"Ошибка создания индикатора: {str(e)}")
            # Возвращаем пустой виджет в случае ошибки
            fallback = QWidget()
            fallback.setFixedWidth(4)
            return fallback

    def update_theme(self, theme):
        """Обновляет тему чипа"""
        self.theme = theme
        theme_styles = THEMES[theme]
        
        # Применяем стили к чипу
        chip_styles = theme_styles["CHIP_WIDGET_STYLES"]
        if isinstance(chip_styles, dict):
            chip_styles = chip_styles.get(theme, chip_styles.get("default", ""))
        self.setStyleSheet(chip_styles)
        
        # Обновляем тему иконки
        if hasattr(self, 'icon_label'):
            self.icon_label.set_theme(theme)
        
        # Обновляем стили меток
        theme_label_styles = CHIP_LABEL_STYLES.get(theme, CHIP_LABEL_STYLES["default"])
        login_style = theme_label_styles.get("login", "")
        service_style = theme_label_styles.get("service", "")
        url_style = theme_label_styles.get("url", "")
            
        for label in self.findChildren(QLabel):
            if label.objectName() == "loginLabel":
                label.setStyleSheet(login_style)
            elif label.objectName() == "serviceLabel":
                label.setStyleSheet(service_style)
            elif label.objectName() == "urlLabel":
                label.setStyleSheet(url_style)

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