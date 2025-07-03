from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import requests
import os
from utils.url_utils import extract_domain
from utils.hash_utils import md5_hash
from styles.themes import THEMES

class IconLoader(QThread):
    icon_loaded = pyqtSignal(str, str)  # url, path

    def __init__(self, url, cache_dir):
        super().__init__()
        self.url = url
        self.cache_dir = cache_dir

    def run(self):
        try:
            domain = extract_domain(self.url)
            if not domain:
                self.icon_loaded.emit(self.url, "")
                return

            hash_name = md5_hash(domain)
            cache_path = os.path.join(self.cache_dir, f"{hash_name}.png")

            # Если иконка уже в кэше, просто возвращаем путь
            if os.path.exists(cache_path):
                self.icon_loaded.emit(self.url, cache_path)
                return

            # Загружаем иконку
            response = requests.get(
                f"https://www.google.com/s2/favicons?domain={domain}&sz=40",
                timeout=3
            )
            if response.status_code == 200:
                with open(cache_path, 'wb') as f:
                    f.write(response.content)
                self.icon_loaded.emit(self.url, cache_path)
            else:
                self.icon_loaded.emit(self.url, "")
        except Exception as e:
            print(f"Error loading favicon: {str(e)}")
            self.icon_loaded.emit(self.url, "")

class LazyIconLabel(QLabel):
    def __init__(self, cache_dir, theme="default", parent=None):
        super().__init__(parent)
        self.cache_dir = cache_dir
        self.url = None
        self.loader = None
        self.default_text = "?"
        self.theme = theme
        self.setFixedSize(70, 50)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._setup_default_style()

    def _setup_default_style(self):
        theme_styles = THEMES[self.theme]["LAZY_ICON_STYLES"]
        self.setStyleSheet(theme_styles["default"])

    def set_theme(self, theme):
        self.theme = theme
        if not self.url:
            self._set_no_url_icon()
        else:
            self._setup_default_style()

    def set_url(self, url, service_name=""):
        if not url:
            self._set_no_url_icon()
            return

        if url == self.url:
            return

        self.url = url
        self.setText(service_name[0].upper() if service_name else "?")

        # Проверяем кэш
        domain = extract_domain(url)
        if domain:
            hash_name = md5_hash(domain)
            cache_path = os.path.join(self.cache_dir, f"{hash_name}.png")

            if os.path.exists(cache_path):
                self._set_icon(cache_path)
                return

        # Запускаем загрузку в фоне
        if self.loader:
            self.loader.quit()

        self.loader = IconLoader(url, self.cache_dir)
        self.loader.icon_loaded.connect(self._on_icon_loaded)
        self.loader.start()

    def _on_icon_loaded(self, url, path):
        if url != self.url:  # Проверяем, что URL не изменился
            return

        if path:
            self._set_icon(path)
        else:
            self._set_no_url_icon()

    def _set_icon(self, path):
        icon = QIcon(path)
        self.setPixmap(icon.pixmap(40, 40))

    def _set_no_url_icon(self):
        theme_styles = THEMES[self.theme]["LAZY_ICON_STYLES"]
        self.setStyleSheet(theme_styles["no_url"])
        self.setText("")  # Убираем текст, так как будет показываться изображение