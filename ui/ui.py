from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QListWidget,
    QInputDialog, QProgressBar, QComboBox, QFileDialog,
    QMessageBox, QDialog, QSpinBox, QStackedWidget, QGroupBox, QTextEdit,
    QSplitter, QLayout, QLayoutItem, QSizePolicy, QScrollArea, QToolButton, QRadioButton, QSpacerItem, QTreeWidget, QListWidgetItem,
    QApplication
)
from PyQt6.QtGui import QMouseEvent, QPixmap, QDrag, QColor, QPainter, QPen, QBrush, QIcon
from PyQt6.QtCore import (
    Qt, QPoint, QMimeData, pyqtSignal, QRect, QSize, QTimer,
    QPropertyAnimation, QEasingCurve, pyqtProperty, QEvent, QProcess
)
import sys
import utils
import os
import json
from password_generator import PasswordGeneratorDialog
from auth.password_manager import PasswordManager
from auth.user_credentials import UserCredentials
from addPassword import AuthWidget
from styles import APP_STYLES, SEARCH_STYLES, NOTES_STYLES, WINDOW_CONTROL_STYLES, SETTINGS_GROUPBOX_STYLES
from utils.url_utils import extract_domain
from utils.hash_utils import md5_hash
from utils.password_utils import password_strength
import requests
import time
from widgets.animated_stack import AnimatedStackedWidget
from widgets.password_status import PasswordStatusWidget
from utils.password_checker import HIBPChecker
from utils.settings_manager import SettingsManager
from utils.cache_manager import CacheManager
from widgets.base_widgets import ToolbarWidget, DraggablePanel
from widgets.password_widgets import TagsContainer, ChipWidget
from widgets.animated_panel import AnimatedPanel
from widgets.overlay_message import OverlayMessage
from styles.themes import THEMES

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


class PasswordManagerUI(QMainWindow):
    def __init__(self, styles):
        super().__init__()
        self.current_theme = "default"
        self.theme_styles = THEMES[self.current_theme]
        self.styles = self.theme_styles["APP_STYLES"]
        self.window_control_styles = self.theme_styles["WINDOW_CONTROL_STYLES"]
        self.password_manager = None
        self.passwords = []
        self.user_credentials = UserCredentials()
        self.normal_geometry = None
        self.settings_visible = False
        
        # Инициализируем менеджер настроек
        self.settings_manager = SettingsManager()
        
        # Инициализируем менеджер кэша
        self.cache_manager = CacheManager(self.settings_manager)
        
        # Кэш для favicon'ок
        self.favicon_cache = {}
        # Обновленный путь к кэшу
        self.favicon_cache_dir = os.path.join(os.path.dirname(__file__), "app_cache", "favicons")
        os.makedirs(self.favicon_cache_dir, exist_ok=True)
        
        # Инициализируем чекер паролей
        self.hibp_checker = HIBPChecker()
        self.hibp_checker.status_ready.connect(self._update_password_status)
        
        # Инициализация стека для переключения между интерфейсами
        self.main_stack = AnimatedStackedWidget(self)
        self.setCentralWidget(self.main_stack)
        
        # Инициализация таймера автоблокировки
        self.autolock_timer = QTimer(self)
        self.autolock_timer.timeout.connect(self.lock_application)
        self.update_autolock_timer()

        # Инициализация оверлея для сообщений
        self.overlay_message = OverlayMessage(self)

        self.init_ui()
        self.init_auth_widget()
        self.connect_signals()
        
        # Применяем сохраненные настройки
        self.apply_saved_settings()
        
        # Инициализируем анимацию правой панели
        self.panel_animator = AnimatedPanel(self.right_panel, self.main_splitter)

    def apply_saved_settings(self):
        """Применяет сохраненные настройки"""
        # Применяем стиль кнопок
        button_style = self.settings_manager.get_setting("appearance", "button_style")
        if button_style == "macOS style":
            self.mac_style_radio.setChecked(True)
        else:
            self.win_style_radio.setChecked(True)
        
        # Применяем время автоблокировки (конвертируем минуты в секунды)
        autolock_minutes = self.settings_manager.get_setting("security", "autolock_minutes")
        self.autolock_spin.setValue(int(autolock_minutes * 60))

    def set_theme(self, theme_name):
        self.current_theme = theme_name
        self.theme_styles = THEMES[theme_name]
        self.styles = self.theme_styles["APP_STYLES"]
        self.window_control_styles = self.theme_styles["WINDOW_CONTROL_STYLES"]
        # Применяем стили к основным элементам
        if hasattr(self, 'tags_container'):
            print("Applying theme to tags_container:", theme_name)
            print("Theme styles for tags:", self.theme_styles["TAGS_CONTAINER_STYLES"])
            self.tags_container.setStyleSheet(self.theme_styles["TAGS_CONTAINER_STYLES"])
            # Обновляем стили всех ChipWidget
            if hasattr(self.tags_container, 'update_chip_styles'):
                chip_styles = self.theme_styles["CHIP_STYLES"]
                if isinstance(chip_styles, dict) and 'default' in chip_styles:
                    self.tags_container.update_chip_styles(chip_styles['default'])
        if hasattr(self, 'center_panel'):
            self.center_panel.setStyleSheet(self.theme_styles.get("PANEL_STYLES", "background: transparent;"))
        if hasattr(self, 'mac_window_controls'):
            self.mac_window_controls.setStyleSheet(self.theme_styles["WINDOW_CONTROL_STYLES"])
        if hasattr(self, 'search_input'):
            self.search_input.setStyleSheet(self.theme_styles["SEARCH_STYLES"])
        if hasattr(self, 'notes_input'):
            self.notes_input.setStyleSheet(self.theme_styles["NOTES_STYLES"])
        if hasattr(self, 'add_button'):
            self.add_button.setStyleSheet(self.theme_styles["ADD_BUTTON_STYLES"])
        if hasattr(self, 'right_panel'):
            self.right_panel.setStyleSheet(self.theme_styles["PANEL_STYLES"])
        if hasattr(self, 'left_panel'):
            self.left_panel.setStyleSheet(self.theme_styles["PANEL_STYLES"])
        if hasattr(self, 'main_splitter'):
            self.main_splitter.setStyleSheet(self.theme_styles["PANEL_STYLES"])
        if hasattr(self, 'settings_group'):
            self.settings_group.setStyleSheet(self.theme_styles.get("SETTINGS_GROUPBOX_STYLES", ""))
        # Применяем общий стиль к контейнеру
        if hasattr(self, 'centralWidget'):
            cw = self.centralWidget()
            if cw:
                cw.setStyleSheet(self.theme_styles["APP_STYLES"])
        # Обновить дочерние виджеты, если нужно
        self.repaint()

    def init_ui(self):
        self.setWindowTitle("Secure Password Manager")
        self.setGeometry(490, 200, 1000, 600)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Основной контейнер для тулбара и стека
        container = QWidget()
        container.setObjectName("MainContainer")
        container.setStyleSheet(self.styles)
        container.setLayout(QVBoxLayout())
        container.layout().setContentsMargins(5, 5, 5, 5)
        container.layout().setSpacing(0)

        # Toolbar
        self.toolbar_widget = ToolbarWidget(self)
        self.toolbar_widget.setObjectName("Toolbar")
        toolbar_layout = QHBoxLayout(self.toolbar_widget)
        toolbar_layout.setContentsMargins(5, 0, 5, 0)
        toolbar_layout.setSpacing(0)

        # Контейнеры для кнопок управления окном
        left_container = QWidget()
        left_container.setFixedWidth(90)
        left_layout = QHBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        right_container = QWidget()
        right_container.setFixedWidth(90)
        right_layout = QHBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # --- macOS стиль (по умолчанию включён) ---
        window_controls = QHBoxLayout()
        window_controls.setSpacing(8)

        self.close_btn = QPushButton()
        self.close_btn.setObjectName("closeButton")
        self.close_btn.setFixedSize(16, 16)
        self.close_btn.clicked.connect(self.close)

        self.maximize_btn = QPushButton()
        self.maximize_btn.setObjectName("maximizeButton")
        self.maximize_btn.setFixedSize(16, 16)
        self.maximize_btn.clicked.connect(self.toggle_maximized)

        self.minimize_btn = QPushButton()
        self.minimize_btn.setObjectName("minimizeButton")
        self.minimize_btn.setFixedSize(16, 16)
        self.minimize_btn.clicked.connect(self.showMinimized)

        window_controls.addWidget(self.close_btn)
        window_controls.addWidget(self.maximize_btn)
        window_controls.addWidget(self.minimize_btn)

        self.mac_window_controls = QWidget()
        self.mac_window_controls.setLayout(window_controls)
        self.mac_window_controls.setStyleSheet(self.window_control_styles)
        left_layout.addWidget(self.mac_window_controls)

        # --- Windows стиль ---
        self.window_controls_win = QWidget()
        win_layout = QHBoxLayout(self.window_controls_win)
        win_layout.setContentsMargins(0, 0, 0, 4)
        win_layout.setSpacing(0)

        self.win_minimize_btn = QPushButton("-")
        self.win_maximize_btn = QPushButton("□")
        self.win_close_btn = QPushButton("✕")

        for btn in [self.win_minimize_btn, self.win_maximize_btn, self.win_close_btn]:
            btn.setFixedSize(30, 30)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: white;
                    border-left: 1px solid #444;
                    font-size: 20px;
                    font-weight: bold;
                    padding: 0px;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.15);
                }
            """)

        self.win_minimize_btn.clicked.connect(self.showMinimized)
        self.win_maximize_btn.clicked.connect(self.toggle_maximized)
        self.win_close_btn.clicked.connect(self.close)

        win_layout.addWidget(self.win_minimize_btn)
        win_layout.addWidget(self.win_maximize_btn)
        win_layout.addWidget(self.win_close_btn)
        right_layout.addWidget(self.window_controls_win)
        self.window_controls_win.hide()

        # Поиск
        search_container = QWidget()
        search_container.setFixedWidth(300)
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(0)
        
        # Поле поиска
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setStyleSheet(self.theme_styles["SEARCH_STYLES"])

        # Добавляем поле поиска в контейнер
        search_layout.addWidget(self.search_input)

        # Добавляем элементы в тулбар
        toolbar_layout.addWidget(left_container)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(search_container, alignment=Qt.AlignmentFlag.AlignCenter)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(right_container)

        # Добавляем тулбар и стек в основной контейнер
        container.layout().addWidget(self.toolbar_widget)
        container.layout().addWidget(self.main_stack)
        self.setCentralWidget(container)

        # Основной виджет с разделителями
        main_widget = QWidget()
        main_widget.setObjectName("CentralWidget")
        main_widget.setStyleSheet(self.styles)

        # Главный горизонтальный разделитель
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter.setHandleWidth(1)  # делаем разделитель тоньше
        self.main_splitter.setChildrenCollapsible(True)  # Разрешаем схлопывание панелей
        self.main_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #404040;
            }
        """)
        
        # Левая панель (категории/настройки)
        self.left_panel = DraggablePanel()
        self.left_panel.setMinimumWidth(0)
        self.left_panel.setMaximumWidth(200)
        self.left_panel.setFixedWidth(200)  # Фиксированная ширина
        self.left_panel.setObjectName("LeftPanel")
        left_layout = QVBoxLayout(self.left_panel)
        left_layout.setContentsMargins(10, 20, 10, 20)
        left_layout.setSpacing(15)

        # Стек для категорий и настроек
        self.left_stack = QStackedWidget()
        left_layout.addWidget(self.left_stack)

        # Центральная панель (список паролей)
        center_panel = QWidget()
        center_panel.setObjectName("CenterPanel")
        center_panel.setMinimumWidth(400)  # Минимальная ширина центральной панели
        center_layout = QVBoxLayout(center_panel)
        center_layout.setContentsMargins(0, 10, 0, 0)
        center_layout.setSpacing(0)

        # Сохраняем ссылку на центральную панель
        self.center_panel = center_panel

        # Список паролей
        self.tags_container = TagsContainer()
        print("Tags container created")  # Отладка
        center_layout.addWidget(self.tags_container)

        # Добавляем кнопку "+" снизу
        add_button_container = QWidget()
        add_button_layout = QHBoxLayout(add_button_container)
        add_button_layout.setContentsMargins(20, 10, 20, 20)
        
        self.add_button = QPushButton("+")
        print("Add button created")  # Отладка
        self.add_button.setMinimumHeight(50)
        self.add_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #1DB954;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1ed760;
            }
            QPushButton:pressed {
                background-color: #1aa34a;
            }
        """)
        self.add_button.clicked.connect(self.show_add_password_panel)
        add_button_layout.addWidget(self.add_button)
        
        center_layout.addWidget(add_button_container)

        # Правая панель (поля ввода)
        self.right_panel = DraggablePanel()
        print("Right panel created")  # Отладка
        self.right_panel.setObjectName("RightPanel")
        self.right_panel.setMinimumWidth(0)
        self.right_panel.setMaximumWidth(250)
        self.right_panel.setFixedWidth(0)  # Начальная ширина 0
        self.right_panel.hide()  # Скрываем панель изначально
        right_layout = QVBoxLayout(self.right_panel)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(10)

        # Добавляем панели в сплиттер
        self.main_splitter.addWidget(self.left_panel)
        self.main_splitter.addWidget(center_panel)
        self.main_splitter.addWidget(self.right_panel)
        self.main_splitter.setSizes([200, 500, 0])  # Начальные размеры
        self.main_splitter.setCollapsible(2, True)  # Разрешаем схлопывание правой панели
        self.main_splitter.setStretchFactor(1, 1)  # Центральная панель растягивается

        # Инициализируем аниматор панели
        self.panel_animator = AnimatedPanel(self.right_panel, self.main_splitter)
        print("Panel animator initialized")  # Отладка

        # Основной layout
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.main_splitter)

        # Инициализация содержимого панелей
        self.init_left_panel_content()
        self.init_right_panel_content()
        
        # Добавляем основной виджет в стек
        self.main_stack.addWidget(main_widget)
        self.main_stack.setCurrentWidget(main_widget)

    def apply_window_button_style(self):
        if self.mac_style_radio.isChecked():
            self.mac_window_controls.show()
            self.window_controls_win.hide()
        else:
            self.mac_window_controls.hide()
            self.window_controls_win.show()

    def init_left_panel_content(self):
        """Инициализация содержимого левой панели"""
        # Основной виджет
        self.left_panel_widget = QWidget()
        self.left_panel_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout(self.left_panel_widget)
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(15)
        
        # Кнопки управления
        self.master_password_btn = QPushButton()
        self.master_password_btn.setIcon(QIcon("icons/LogPin.png"))
        self.master_password_btn.setIconSize(QSize(32, 32))
        self.master_password_btn.setFixedSize(32, 32)
        self.master_password_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
        """)

        self.settings_btn = QPushButton()
        self.settings_btn.setIcon(QIcon("icons/settings.png"))
        self.settings_btn.setIconSize(QSize(32, 32))
        self.settings_btn.setFixedSize(32, 32)
        self.settings_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
        """)

        # Кнопки в нижней части
        buttons_bg = QWidget()
        buttons_bg.setFixedHeight(52)
        buttons_bg.setStyleSheet("""
            background-color: rgba(255, 255, 255, 20);
            border: 1px solid #404040;
            border-radius: 7px;
        """)

        bg_layout = QHBoxLayout(buttons_bg)
        bg_layout.setContentsMargins(8, 8, 8, 8)
        bg_layout.setSpacing(10)
        bg_layout.addWidget(self.master_password_btn)
        bg_layout.addWidget(self.settings_btn)
        bg_layout.addStretch()

        # Добавляем кнопки в основной layout
        layout.addStretch()  # Добавляем растяжку сверху
        layout.addWidget(buttons_bg)  # Кнопки будут прижаты к низу

        # Панель настроек
        self.settings_panel = QWidget()
        self.settings_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        settings_layout = QVBoxLayout(self.settings_panel)
        settings_layout.setContentsMargins(10, 10, 10, 10)
        settings_layout.setSpacing(15)

        # --- Новый общий контейнер для всех настроек ---
        settings_group = QGroupBox("Settings")
        settings_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        settings_group_layout = QVBoxLayout()
        settings_group_layout.setSpacing(20)
        settings_group_layout.setContentsMargins(10, 10, 10, 10)
        settings_group.setStyleSheet(SETTINGS_GROUPBOX_STYLES)

        # Appearance секция
        appearance_label = QLabel("Appearance")
        appearance_label.setStyleSheet("font-weight: bold; font-size: 15px; margin-bottom: 4px;")
        settings_group_layout.addWidget(appearance_label)
        # Theme radio
        theme_layout = QHBoxLayout()
        self.default_theme_radio = QRadioButton("Default")
        self.cyberpunk_theme_radio = QRadioButton("Cyberpunk")
        self.default_theme_radio.setChecked(self.current_theme == "default")
        self.cyberpunk_theme_radio.setChecked(self.current_theme == "cyberpunk")
        theme_layout.addWidget(self.default_theme_radio)
        theme_layout.addWidget(self.cyberpunk_theme_radio)
        settings_group_layout.addLayout(theme_layout)
        # Window controls radio
        window_controls_label = QLabel("Window controls")
        window_controls_label.setStyleSheet("font-size: 13px; margin-top: 8px;")
        settings_group_layout.addWidget(window_controls_label)
        window_controls_layout = QHBoxLayout()
        self.mac_style_radio = QRadioButton("macOS style")
        self.win_style_radio = QRadioButton("Windows style")
        self.mac_style_radio.setChecked(True)
        window_controls_layout.addWidget(self.mac_style_radio)
        window_controls_layout.addWidget(self.win_style_radio)
        settings_group_layout.addLayout(window_controls_layout)

        # Security секция
        security_label = QLabel("Security")
        security_label.setStyleSheet("font-weight: bold; font-size: 15px; margin-top: 12px; margin-bottom: 4px;")
        settings_group_layout.addWidget(security_label)
        autolock_layout = QHBoxLayout()
        autolock_label = QLabel("Auto-lock after:")
        self.autolock_spin = QSpinBox()
        self.autolock_spin.setRange(5, 3600)
        self.autolock_spin.setSuffix(" seconds")
        autolock_layout.addWidget(autolock_label)
        autolock_layout.addWidget(self.autolock_spin)
        settings_group_layout.addLayout(autolock_layout)

        # Data секция
        data_label = QLabel("Data")
        data_label.setStyleSheet("font-weight: bold; font-size: 15px; margin-top: 12px; margin-bottom: 4px;")
        settings_group_layout.addWidget(data_label)
        data_layout = QVBoxLayout()
        self.export_btn = QPushButton("Export")
        self.import_btn = QPushButton("Import")
        data_layout.addWidget(self.export_btn)
        data_layout.addWidget(self.import_btn)
        settings_group_layout.addLayout(data_layout)

        settings_group.setLayout(settings_group_layout)
        settings_layout.addWidget(settings_group)

        # Кнопка возврата
        self.back_btn = QPushButton("Back")
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #2D2D2D;
                color: white;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 8px 16px;
                min-height: 32px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #383838;
                border-color: #505050;
            }
            QPushButton:pressed {
                background-color: #252525;
            }
        """)
        settings_layout.addWidget(self.back_btn)

        # Стек панелей
        self.left_stack.addWidget(self.left_panel_widget)
        self.left_stack.addWidget(self.settings_panel)
        
        # Создаем контейнер для стека с правильным layout
        stack_container = QWidget()
        stack_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        stack_layout = QVBoxLayout(stack_container)
        stack_layout.setContentsMargins(0, 0, 0, 0)
        stack_layout.setSpacing(0)
        stack_layout.addWidget(self.left_stack)
        
        self.left_panel.layout().addWidget(stack_container)

    def init_right_panel_content(self):
        """Инициализация содержимого правой панели"""
        content_widget = QWidget()
        input_group = QGroupBox("")
        input_group_layout = QVBoxLayout(input_group)
        input_group.setStyleSheet("""
            QGroupBox {
                background-color: transparent;
                border-radius: 0px;
            }
                    QLabel[required="true"] {
                color: #ffffff;
            }
            QLabel[required="true"]::after {
                content: " *";
                color: #ff5555;
            }
        """)

        self.service_input = QLineEdit(placeholderText="")
        self.url_input = QLineEdit(placeholderText="")
        self.login_input = QLineEdit(placeholderText="")
        self.email_input = QLineEdit(placeholderText="")
        self.phone_input = QLineEdit(placeholderText="")

        # notes
        self.notes_input = QTextEdit()
        self.notes_input.setStyleSheet(NOTES_STYLES)  # Применяем стили для заметок
        self.notes_input.setFixedHeight(80)

        # Кнопки
        control_panel = QHBoxLayout()
        self.add_btn = QPushButton("Save")
        self.generate_btn = QPushButton("Generate")

        # Поле пароля с глазиком внутри
        password_container = QWidget()
        password_layout = QHBoxLayout(password_container)
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(5)

        # Создаем контейнер для метки "Password" и статуса
        password_label_container = QWidget()
        password_label_layout = QHBoxLayout(password_label_container)
        password_label_layout.setContentsMargins(0, 0, 0, 0)
        password_label_layout.setSpacing(5)

        # Создаем метки с указанием обязательных полей
        service_label = QLabel("Сервис")
        service_label.setProperty("required", True)
        login_label = QLabel("Логин")
        login_label.setProperty("required", True)
        password_label = QLabel("Пароль")
        password_label.setProperty("required", True)

        self.password_status = PasswordStatusWidget()
        password_label_layout.addWidget(password_label)
        password_label_layout.addWidget(self.password_status)
        password_label_layout.addStretch()

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet(APP_STYLES)

        self.toggle_btn = QToolButton()
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setIcon(QIcon("icons/eye2.png"))
        self.toggle_btn.setIconSize(QSize(22, 22))
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_btn.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                border: none;
                padding: 0px;
            }
        """)
        
        # Подключаем сигнал сразу после создания кнопки
        self.toggle_btn.toggled.connect(self.toggle_visibility)

        # Расположение кнопки внутри поля
        def reposition_eye_icon():
            height = self.password_input.height()
            btn_size = self.toggle_btn.sizeHint()
            self.toggle_btn.move(
                self.password_input.width() - btn_size.width() - 6,
                (height - btn_size.height()) // 2
            )

        original_resize = self.password_input.resizeEvent

        def password_input_resize(event):
            original_resize(event)
            reposition_eye_icon()

        self.password_input.resizeEvent = password_input_resize
        self.toggle_btn.setParent(self.password_input)
        password_layout.addWidget(self.password_input)

        # Сборка всего
        input_group_layout.addWidget(service_label)
        input_group_layout.addWidget(self.service_input)
        input_group_layout.addWidget(QLabel("URL"))
        input_group_layout.addWidget(self.url_input)
        input_group_layout.addWidget(login_label)
        input_group_layout.addWidget(self.login_input)
        input_group_layout.addWidget(password_label_container)
        input_group_layout.addWidget(password_container)
        input_group_layout.addWidget(QLabel("Email"))
        input_group_layout.addWidget(self.email_input)
        input_group_layout.addWidget(QLabel("Телефон"))
        input_group_layout.addWidget(self.phone_input)
        input_group_layout.addWidget(QLabel("Заметки"))
        input_group_layout.addWidget(self.notes_input)
        input_group_layout.addLayout(control_panel)
        control_panel.addWidget(self.add_btn)
        control_panel.addWidget(self.generate_btn)

        self.right_panel.add_content(input_group)
        self.right_panel.layout().addStretch()

    def connect_signals(self):
        """Подключение сигналов"""
        print("Connecting signals...")  # Отладка
        
        # Основные сигналы
        self.search_input.textChanged.connect(self.update_list)
        self.add_btn.clicked.connect(self.save_password)
        self.generate_btn.clicked.connect(self.show_password_generator)
        self.master_password_btn.clicked.connect(self.show_password_change)
        self.settings_btn.clicked.connect(self.show_settings_view)
        self.back_btn.clicked.connect(self.show_main_view)
        
        # Кнопка добавления нового пароля
        self.add_button.clicked.connect(self.show_add_password_panel)
        print("Add button connected")  # Отладка
        
        # Подключаем обработчик клика по тегу
        self.tags_container.tag_clicked.connect(self.on_tag_clicked)
        print("Tag click handler connected")  # Отладка

        # Settings connections
        self.mac_style_radio.toggled.connect(self._on_button_style_changed)
        self.win_style_radio.toggled.connect(self._on_button_style_changed)
        self.autolock_spin.valueChanged.connect(self._on_autolock_changed)

        # Добавляем проверку пароля при изменении
        self.password_input.textChanged.connect(self.check_password_security)
        
        # Добавляем обработчик изменения размеров сплиттера
        self.main_splitter.splitterMoved.connect(self._on_splitter_moved)
        
        # Добавляем обработчики для сброса таймера при активности
        for widget in self.findChildren(QWidget):
            if isinstance(widget, (QLineEdit, QPushButton, QComboBox)):
                widget.installEventFilter(self)
        print("Event filters installed")  # Отладка

        # Подключаем сигналы для тем
        self.default_theme_radio.toggled.connect(lambda checked: checked and self.set_theme("default"))
        self.cyberpunk_theme_radio.toggled.connect(lambda checked: checked and self.set_theme("cyberpunk"))

    def eventFilter(self, obj, event):
        """Фильтр событий для отслеживания активности пользователя"""
        if event.type() in [QEvent.Type.MouseButtonPress, QEvent.Type.KeyPress]:
            self.reset_autolock_timer()
        return super().eventFilter(obj, event)

    def show_settings(self):
        """Показывает диалог настроек"""
        self.left_stack.setCurrentWidget(self.settings_panel)
        self.settings_btn.hide()

    def _on_button_style_changed(self, checked):
        """Обработчик изменения стиля кнопок"""
        if not checked:  # Реагируем только на включение радиокнопки
            return
        
        style = "macOS style" if self.mac_style_radio.isChecked() else "Windows style"
        self.settings_manager.set_setting("appearance", "button_style", style)
        self.apply_window_button_style()

    def _on_autolock_changed(self, value):
        """Обработчик изменения времени автоблокировки"""
        # Конвертируем секунды в минуты
        minutes = value / 60.0
        self.settings_manager.set_setting("security", "autolock_minutes", minutes)
        self.update_autolock_timer()

    def update_autolock_timer(self):
        """Обновляет таймер автоблокировки"""
        minutes = self.settings_manager.get_setting("security", "autolock_minutes")
        print(f"Updating autolock timer: {minutes} minutes")  # Отладка
        
        # Останавливаем предыдущий таймер
        if self.autolock_timer.isActive():
            self.autolock_timer.stop()
        
        if minutes > 0 and self.password_manager is not None:
            milliseconds = int(minutes * 60 * 1000)  # Преобразуем в миллисекунды
            print(f"Starting timer for {milliseconds}ms")  # Отладка
            self.autolock_timer.setInterval(milliseconds)
            self.autolock_timer.start()
            print("Timer started")  # Отладка
        else:
            print("Timer not started (minutes <= 0 or no password manager)")  # Отладка

    def show_password_change(self):
        """Показывает окно установки/изменения учетных данных"""
        saved_username = self.user_credentials.get_saved_username() or ""
        
        # Создаем новый виджет аутентификации
        self.auth_widget = AuthWidget(username=saved_username, is_password_change=True, main_window=self)
        self.auth_widget.accepted.connect(self.handle_password_change)
        
        # Сначала добавляем виджет в стек
        self.main_stack.addWidget(self.auth_widget)
        # Затем переключаемся на него
        self.main_stack.setCurrentWidget(self.auth_widget)
        
        # Добавляем обработчик для очистки стека при закрытии
        def cleanup():
            self.main_stack.removeWidget(self.auth_widget)
            self.auth_widget.deleteLater()
        
        self.auth_widget.accepted.connect(cleanup)

    def handle_password_change(self):
        """Обработчик смены учетных данных"""
        username, new_pin = self.auth_widget.get_credentials()
        old_username = self.user_credentials.get_saved_username()
        
        try:
            # Проверяем, изменилось ли имя пользователя
            username_changed = old_username != username
            
            if username_changed:
                # Сначала меняем имя пользователя
                if not self.password_manager.change_username(username):
                    raise Exception("Ошибка при смене имени пользователя")
            
            # Затем меняем PIN в менеджере паролей
            if not self.password_manager.change_password(new_pin):
                raise Exception("Ошибка при смене пароля в менеджере")
            
            # Обновляем учетные данные
            self.user_credentials.save_credentials(username, new_pin)
            
            # Обновляем список паролей
            self.passwords = self.password_manager.passwords
            self.update_list()
            
            message = "Учетные данные успешно обновлены!" if username_changed else "PIN успешно изменен!"
            self.show_temporary_message(message, duration=2500)
            self.main_stack.setCurrentIndex(0)  # Возвращаемся к основному интерфейсу
            
        except Exception as e:
            self.show_temporary_message(f"Ошибка при обновлении учетных данных: {str(e)}", duration=3500)
            print(f"Ошибка обновления учетных данных: {str(e)}")

    def show_password_generator(self):
        """Открывает диалог генератора паролей"""
        dialog = PasswordGeneratorDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            password = dialog.get_password()
            if password:
                self.password_input.setText(password)
                self.password_input.setFocus()

    def toggle_maximized(self):
        if self.isMaximized():
            self.showNormal()
            if self.normal_geometry:
                self.setGeometry(self.normal_geometry)
        else:
            self.normal_geometry = self.geometry()
            self.showMaximized()

    def toggle_visibility(self, checked):
        if checked:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_btn.setIcon(QIcon("icons/eye1.png"))  # иконка "показать"
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_btn.setIcon(QIcon("icons/eye2.png"))  # иконка "скрыть"

    def show_temporary_message(self, text: str, duration: int = 3000, message_type: str = 'default'):
        """Показывает временное сообщение"""
        if message_type == 'error':
            self.overlay_message.show_error(text, duration)
        elif message_type == 'warning':
            self.overlay_message.show_warning(text, duration)
        elif message_type == 'success':
            self.overlay_message.show_success(text, duration)
        else:
            self.overlay_message.show_message(text, duration)

    def show_lock_message(self, text: str):
        """Показывает сообщение о блокировке"""
        self.overlay_message.show_warning(text, duration=0)  # duration=0 означает, что сообщение не исчезнет автоматически

    def lock_application(self):
        """Блокирует приложение"""
        if self.password_manager is None:
            return
            
        print("Locking application due to inactivity")
            
        try:
            # Сохраняем все несохраненные изменения
            if hasattr(self, 'right_panel') and self.right_panel.isVisible():
                self.panel_animator.animate(show=False)
            
            # Очищаем конфиденциальные данные
            self.clear_sensitive_data()
            
            # Сохраняем имя пользователя для повторного входа
            saved_username = self.user_credentials.get_saved_username()
            
            # Создаем новый виджет аутентификации
            self.auth_widget = AuthWidget(
                username=saved_username,
                is_first_launch=False,
                main_window=self  # Добавляем ссылку на главное окно
            )
            self.auth_widget.accepted.connect(self.handle_pin_entry)
            
            # Добавляем виджет в стек и переключаемся на него
            self.main_stack.addWidget(self.auth_widget)
            self.main_stack.setCurrentWidget(self.auth_widget)
            
            # Останавливаем таймер
            if self.autolock_timer.isActive():
                self.autolock_timer.stop()
            
            # Показываем сообщение о блокировке
            self.overlay_message.show_message("Приложение заблокировано\nНажмите для продолжения", duration=0)
            
        except Exception as e:
            print(f"Error during application lock: {str(e)}")
            # В случае ошибки всё равно блокируем приложение
            self.clear_sensitive_data()
            self.overlay_message.show_message("Приложение заблокировано", duration=0)

    def clear_sensitive_data(self):
        """Очищает конфиденциальные данные из памяти"""
        try:
            print("Clearing sensitive data")
            
            # Очищаем поля ввода
            sensitive_widgets = [
                'password_input', 'service_input', 'login_input',
                'url_input', 'email_input', 'phone_input', 'notes_input'
            ]
            
            for widget_name in sensitive_widgets:
                if hasattr(self, widget_name):
                    widget = getattr(self, widget_name)
                    if isinstance(widget, QTextEdit):
                        widget.clear()
                        # Принудительно очищаем буфер отмены
                        widget.setUndoRedoEnabled(False)
                        widget.setUndoRedoEnabled(True)
                    else:
                        widget.clear()
                        # Принудительно очищаем историю
                        widget.setText("")
            
            # Очищаем список паролей
            if hasattr(self, 'passwords'):
                self.passwords.clear()
                self.passwords = []
            
            # Очищаем теги
            if hasattr(self, 'tags_container'):
                self.tags_container.clear()
            
            # Очищаем менеджер паролей
            if self.password_manager:
                self.password_manager.clear_sensitive_data()  # Предполагается, что такой метод существует
                self.password_manager = None
            
            # Принудительно вызываем сборщик мусора
            import gc
            gc.collect()
            
        except Exception as e:
            print(f"Error during sensitive data cleanup: {str(e)}")
            # В случае ошибки пытаемся очистить хотя бы критические данные
            if hasattr(self, 'password_input'):
                self.password_input.clear()
            if hasattr(self, 'passwords'):
                self.passwords.clear()
            if self.password_manager:
                self.password_manager = None

    def handle_pin_entry(self):
        """Обработчик повторного входа после блокировки"""
        try:
            # Получаем введенные учетные данные
            username, pin = self.auth_widget.get_credentials()
            
            # Проверяем учетные данные
            if not self.user_credentials.verify_credentials(username, pin):
                self.overlay_message.show_message("Неверный PIN-код", message_type='error')
                return
            
            # Создаем новый менеджер паролей
            self.password_manager = PasswordManager(username, pin)
            
            # Удаляем виджет аутентификации из стека
            self.main_stack.removeWidget(self.auth_widget)
            self.auth_widget.deleteLater()
            self.auth_widget = None
            
            # Возвращаемся к основному интерфейсу
            self.main_stack.setCurrentIndex(0)
            
            # Обновляем список паролей
            self.update_list()
            
            # Запускаем таймер автоблокировки
            self.update_autolock_timer()
            
            # Скрываем сообщение о блокировке
            self.overlay_message.hide()
            
        except Exception as e:
            print(f"Error during pin entry: {str(e)}")
            self.overlay_message.show_message(
                "Ошибка при входе в систему",
                message_type='error'
            )

    def mousePressEvent(self, event):
        """Обработчик нажатия мыши"""
        super().mousePressEvent(event)
        self.reset_autolock_timer()

    def keyPressEvent(self, event):
        """Обработчик нажатия клавиш"""
        super().keyPressEvent(event)
        self.reset_autolock_timer()

    def reset_autolock_timer(self):
        """Сбрасывает таймер автоблокировки при активности пользователя"""
        if self.autolock_timer.isActive():
            print("Resetting autolock timer")  # Отладка
            self.autolock_timer.stop()
            self.autolock_timer.start()

    def on_tag_clicked(self, entry_data):
        """Обработчик клика по тегу"""
        print("on_tag_clicked called")  # Отладка
        
        # Заполняем все возможные поля из entry_data
        fields_mapping = {
            'service': self.service_input,
            'url': self.url_input,
            'login': self.login_input,
            'password': self.password_input,
            'email': self.email_input,
            'phone': self.phone_input,
            'notes': self.notes_input
        }
        
        # Очищаем все поля перед заполнением
        self.clear_fields()
        
        # Заполняем поля данными
        for field, widget in fields_mapping.items():
            if field in entry_data:
                if isinstance(widget, QTextEdit):
                    widget.setPlainText(str(entry_data[field]))
                else:
                    widget.setText(str(entry_data[field]))
        
        # Показываем панель
        self.panel_animator.animate(show=True)

    def show_settings_view(self):
        """Переключает на вид настроек"""
        self.left_stack.setCurrentWidget(self.settings_panel)
        self.settings_btn.hide()

    def show_main_view(self):
        """Возвращает к основному виду"""
        self.left_stack.setCurrentWidget(self.left_panel_widget)
        self.settings_btn.show()

    def update_list(self, filtered_passwords=None):
        """Обновляет список паролей с учетом фильтров"""
        print("Updating password list")  # Отладка
        
        # Очищаем предыдущие теги
        self.tags_container.clear()

        # Если менеджер паролей не инициализирован, выходим
        if not self.password_manager:
            print("Password manager not initialized")  # Отладка
            return

        search_text = self.search_input.text().lower().strip()
        
        # Получаем отфильтрованные пароли
        passwords = self.password_manager.filter_entries(search_text=search_text)
        print(f"Found {len(passwords)} passwords")  # Отладка
        
        # Создаем все чипы сразу
        for entry in passwords:
            # Проверяем что entry является словарем
            if not isinstance(entry, dict):
                print(f"Invalid entry type: {type(entry)}")  # Отладка
                continue
                
            # Создаем чип
            print(f"Adding chip for {entry.get('service', 'unknown')}")  # Отладка
            self.tags_container.add_tag(entry)

    def check_password_security(self):
        """Запускает проверку безопасности пароля"""
        password = self.password_input.text()
        self.hibp_checker.check_password(password)

    def _update_password_status(self, status):
        """Обновляет статус пароля в интерфейсе"""
        self.password_status.update_status(status)

    def save_password(self):
        """Сохраняет пароль"""
        try:
            # Скрываем сообщение, если оно показано
            if hasattr(self, 'overlay_message'):
                self.overlay_message.hide()

            # Собираем и валидируем данные
            service = self.service_input.text().strip()
            login = self.login_input.text().strip()
            password = self.password_input.text().strip()
            url = self.url_input.text().strip()
            email = self.email_input.text().strip() if hasattr(self, 'email_input') else ""
            phone = self.phone_input.text().strip() if hasattr(self, 'phone_input') else ""
            notes = self.notes_input.toPlainText().strip()

                        # Проверяем обязательные поля
            if not service:
                self.show_temporary_message("Поле 'Сервис' обязательно для заполнения", message_type='error')
                self.service_input.setFocus()
                return

            if not login:
                self.show_temporary_message("Поле 'Логин' обязательно для заполнения", message_type='error')
                self.login_input.setFocus()
                return

            if not password:
                self.show_temporary_message("Поле 'Пароль' обязательно для заполнения", message_type='error')
                self.password_input.setFocus()
                return

            # Проверяем инициализацию менеджера паролей
            if not self.password_manager:
                raise RuntimeError("Менеджер паролей не инициализирован")

            # Сохраняем пароль
            kwargs = {}
            if url: kwargs["url"] = url
            if email: kwargs["email"] = email
            if phone: kwargs["phone"] = phone
            if notes: kwargs["notes"] = notes

            self.password_manager.save_password(
                service=service,
                password=password,
                login=login,
                **kwargs
            )
            
            # Обновляем список паролей
            self.passwords = self.password_manager.passwords
            self.update_list()
            
            # Очищаем поля
            self.clear_fields()
            
            # Показываем сообщение об успехе
            self.show_temporary_message("Пароль успешно сохранен", message_type='success')
            
            # Скрываем правую панель
            self.panel_animator.animate(show=False)
            
        except ValueError as e:
            # Показываем ошибку валидации
            self.show_temporary_message(str(e), message_type='error')
        except RuntimeError as e:
            # Показываем ошибку инициализации
            self.show_temporary_message(str(e), message_type='error')
        except Exception as e:
            # Показываем общую ошибку
            error_msg = f"Ошибка при сохранении: {str(e)}"
            print(f"Unexpected error in save_password: {str(e)}")
            self.show_temporary_message(error_msg, message_type='error')

    def _on_splitter_moved(self, pos, index):
        """Обработчик изменения размеров сплиттера"""
        print(f"Splitter moved: pos={pos}, index={index}")  # Отладка
        # Проверяем, если правая панель стала слишком узкой
        if self.right_panel.width() < 50:  # Порог схлопывания
            print("Panel width below threshold, collapsing")  # Отладка
            self.panel_animator.animate(show=False)  # Скрываем панель
        
        # Скрываем сообщение, если оно показано
        if hasattr(self, 'overlay_message'):
            self.overlay_message.hide()

    def update_panel_styles(self):
        """Обновляет стили панелей после перемещения"""
        # Обновляем стили границ в зависимости от позиции
        left_index = self.main_splitter.indexOf(self.left_panel)
        right_index = self.main_splitter.indexOf(self.right_panel)
        
        # Стили для левой панели
        self.left_panel.setStyleSheet("""
            #LeftPanel {
                border-right: 1px solid #404040;
                border-top: 1px solid #404040;
                background-color: transparent;
            }
        """)
        
        # Стили для правой панели
        self.right_panel.setStyleSheet("""
            #RightPanel {
                border-left: 1px solid #404040;
                border-top: 1px solid #404040;
                background-color: transparent;
            }
        """)
        
        # Скрываем сообщение, если оно показано
        if hasattr(self, 'overlay_message'):
            self.overlay_message.hide()

    def show_add_password_panel(self):
        """Показывает правую панель для добавления нового пароля"""
        try:
            print("show_add_password_panel called")
            
            # Проверяем состояние менеджера паролей
            if not self.password_manager:
                self.show_temporary_message("Необходимо войти в систему", message_type='warning')
                return
                
            # Проверяем, не идёт ли уже анимация
            if not hasattr(self, 'panel_animator'):
                print("Panel animator not initialized")
                self.panel_animator = AnimatedPanel(self.right_panel, self.main_splitter)
            
            if self.panel_animator.is_animating():
                print("Animation already in progress, skipping")
                return
            
            # Очищаем поля и показываем панель
            self.clear_fields()
            self.panel_animator.animate(show=True)
            self.service_input.setFocus()
            
        except Exception as e:
            print(f"Error showing add password panel: {str(e)}")
            # В случае ошибки просто показываем панель без анимации
            self.clear_fields()
            self.right_panel.show()
            self.right_panel.setFixedWidth(250)
            self.service_input.setFocus()

    def animate_panel(self, show=True, animate=True):
        """Анимирует появление/скрытие правой панели"""
        try:
            # Проверяем состояние анимации
            if hasattr(self, 'panel_animator') and self.panel_animator.is_animating():
                print("Animation already in progress, skipping")
                return
                
            # Проверяем, схлопнута ли панель
            is_collapsed = self.right_panel.width() == 0
            
            # Если панель схлопнута и мы хотим её показать, всегда используем анимацию
            if show and is_collapsed:
                animate = True
            
            # Сохраняем текущие размеры для восстановления при ошибке
            current_sizes = self.main_splitter.sizes()
            
            if show and not animate:
                self.right_panel.show()
                self.right_panel.setFixedWidth(250)
                # Если панель была схлопнута, восстанавливаем её размер
                if is_collapsed:
                    sizes = self.main_splitter.sizes()
                    sizes[-1] = 250  # Устанавливаем ширину правой панели
                    sizes[-2] = max(400, sizes[-2] - 250)  # Корректируем ширину центральной панели
                    self.main_splitter.setSizes(sizes)
                return
                
            if show:
                self.right_panel.show()  # Показываем панель перед анимацией
                # Если панель была схлопнута, подготавливаем её к анимации
                if is_collapsed:
                    sizes = self.main_splitter.sizes()
                    sizes[-1] = 0  # Начальная ширина правой панели
                    self.main_splitter.setSizes(sizes)
                
            self.panel_animator.animate(show=show, animate=animate)
            
        except Exception as e:
            print(f"Error animating panel: {str(e)}")
            # В случае ошибки восстанавливаем предыдущее состояние
            try:
                self.main_splitter.setSizes(current_sizes)
                if show:
                    self.right_panel.show()
                    self.right_panel.setFixedWidth(250)
                else:
                    self.right_panel.hide()
                    self.right_panel.setFixedWidth(0)
            except Exception as restore_error:
                print(f"Error restoring panel state: {str(restore_error)}")
                # В крайнем случае просто скрываем панель
                self.right_panel.hide()
                self.right_panel.setFixedWidth(0)

    def init_auth_widget(self):
        """Инициализация виджета аутентификации"""
        # Проверяем наличие сохраненных учетных данных
        saved_username = self.user_credentials.get_saved_username()
        is_first_launch = saved_username is None

        # Создаем виджет аутентификации и передаем self как main_window
        self.auth_widget = AuthWidget(
            username=saved_username or "",
            is_first_launch=is_first_launch,  # Используем правильное значение
            is_password_change=False,
            main_window=self
        )

        # Подключаем сигналы
        self.auth_widget.accepted.connect(self._on_auth_accepted)
        self.auth_widget.skipped.connect(self._on_auth_skipped)

        # Добавляем виджет в стек
        self.main_stack.addWidget(self.auth_widget)
        
        # Если это первый запуск, показываем виджет аутентификации
        if is_first_launch:
            self.main_stack.setCurrentWidget(self.auth_widget)
        else:
            # Если есть сохраненные данные, тоже показываем виджет аутентификации
            self.main_stack.setCurrentWidget(self.auth_widget)

    def _on_auth_accepted(self):
        """Обработчик успешной аутентификации"""
        username, pin = self.auth_widget.get_credentials()
        
        try:
            # Сохраняем учетные данные
            self.user_credentials.save_credentials(username, pin)
            
            # Создаем менеджер паролей
            self.password_manager = PasswordManager(username, pin)
            
            # Переключаемся на основной интерфейс
            self.main_stack.setCurrentIndex(0)  # Индекс 0 - это основной интерфейс
            
            # Обновляем список паролей
            self.update_list()
            
            # Запускаем таймер автоблокировки
            self.update_autolock_timer()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось создать пользователя: {str(e)}"
            )

    def _on_auth_skipped(self):
        """Обработчик пропуска аутентификации"""
        # Переключаемся на основной интерфейс без аутентификации
        self.init_main_interface()
        self.main_stack.setCurrentIndex(1)

    def init_main_interface(self):
        """Инициализация основного интерфейса"""
        # Создаем основной виджет
        main_widget = QWidget()
        self.main_stack.addWidget(main_widget)
        
        # Основной layout
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Добавляем заголовок
        header = QLabel("Password Manager")
        header.setStyleSheet("""
            QLabel {
                background-color: #2c3e50;
                color: white;
                padding: 10px;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        main_layout.addWidget(header)
        
        # Добавляем основное содержимое
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Если есть менеджер паролей, показываем список паролей
        if self.password_manager:
            # Здесь будет список паролей
            pass
        else:
            # Показываем сообщение о работе без аутентификации
            message = QLabel("Работа без аутентификации. Функциональность ограничена.")
            message.setStyleSheet("color: #666; font-size: 14px;")
            content_layout.addWidget(message, alignment=Qt.AlignmentFlag.AlignCenter)
        
        main_layout.addWidget(content)

    def get_favicon(self, url):
        """Получает favicon с кэшированием в памяти и на диске"""
        try:
            if not url:
                return ""
                
            # Проверяем кэш в памяти
            if url in self.favicon_cache:
                return self.favicon_cache[url]

            domain = extract_domain(url)
            if not domain:
                return ""

            hash_name = md5_hash(domain)
            cache_path = os.path.join(self.favicon_cache_dir, f"{hash_name}.png")

            # Проверяем кэш на диске
            if os.path.exists(cache_path):
                self.favicon_cache[url] = cache_path
                # Очищаем кэш если превышен лимит
                self.cache_manager.cleanup_favicons()
                return cache_path

            try:
                response = requests.get(
                    f"https://www.google.com/s2/favicons?domain={domain}&sz=32",
                    timeout=3,
                    verify=True  # Проверяем SSL сертификат
                )
                response.raise_for_status()  # Проверяем статус ответа
                
                if response.content:
                    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
                    with open(cache_path, 'wb') as f:
                        f.write(response.content)
                    self.favicon_cache[url] = cache_path
                    # Очищаем кэш если превышен лимит
                    self.cache_manager.cleanup_favicons()
                    return cache_path
                else:
                    raise ValueError("Пустой ответ от сервера")
                    
            except requests.Timeout:
                print(f"Timeout loading favicon for {domain}")
            except requests.RequestException as e:
                print(f"Network error loading favicon: {str(e)}")
            except (IOError, OSError) as e:
                print(f"File system error saving favicon: {str(e)}")
            except Exception as e:
                print(f"Unexpected error loading favicon: {str(e)}")
                
            # Кэшируем отсутствие иконки
            self.favicon_cache[url] = ""
            
        except Exception as e:
            print(f"Critical error in get_favicon: {str(e)}")
            
        return ""

    def closeEvent(self, event):
        """Обработчик закрытия окна"""
        # Очищаем ресурсы
        self.hibp_checker.cleanup()
        # Очищаем кэш при выходе
        self.cache_manager.cleanup_all()
        super().closeEvent(event)

    def check_for_updates(self):
        """Проверка обновлений временно отключена"""
        pass

    def clear_fields(self):
        self.service_input.clear()
        self.url_input.clear()
        self.login_input.clear()
        self.password_input.clear()
        self.email_input.clear()
        self.phone_input.clear()
        self.notes_input.clear()
        # Очищаем статус пароля
        if hasattr(self, 'password_status'):
            self.password_status.update_status({})

