from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import requests
import os
from utils.url_utils import extract_domain
from utils.hash_utils import md5_hash

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
                return
                
            hash_name = md5_hash(domain)
            cache_path = os.path.join(self.cache_dir, f"{hash_name}.png")
            
            # Если иконка уже в кэше, просто возвращаем путь
            if os.path.exists(cache_path):
                self.icon_loaded.emit(self.url, cache_path)
                return
                
            # Загружаем иконку
            response = requests.get(
                f"https://www.google.com/s2/favicons?domain={domain}&sz=32",
                timeout=3
            )
            if response.status_code == 200:
                with open(cache_path, 'wb') as f:
                    f.write(response.content)
                self.icon_loaded.emit(self.url, cache_path)
        except Exception as e:
            print(f"Error loading favicon: {str(e)}")
            self.icon_loaded.emit(self.url, "")

class LazyIconLabel(QLabel):
    def __init__(self, cache_dir, parent=None):
        super().__init__(parent)
        self.cache_dir = cache_dir
        self.url = None
        self.loader = None
        self.default_text = "?"
        self.setFixedSize(28, 28)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._setup_default_style()
        
    def _setup_default_style(self):
        self.setStyleSheet("""
            color: #FFFFFF;
            font-size: 16px;
            font-weight: bold;
            background-color: #2d2d2d;
            border-radius: 6px;
        """)
        
    def set_url(self, url, service_name=""):
        if url == self.url:
            return
            
        self.url = url
        
        # Показываем первую букву сервиса как placeholder
        self.setText(service_name[0].upper() if service_name else "?")
        
        if not url:
            return
            
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
            self.setText(self.default_text)
            
    def _set_icon(self, path):
        icon = QIcon(path)
        self.setPixmap(icon.pixmap(28, 28)) 