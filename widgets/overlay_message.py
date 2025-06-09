from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication
from PyQt6.QtCore import Qt, QTimer
from styles.themes import THEMES

class OverlayMessage(QWidget):
    def __init__(self, parent=None, theme="default"):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.theme = theme
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Применяем базовый стиль
        self.label.setStyleSheet(THEMES[self.theme]["OVERLAY_MESSAGE_STYLES"]["base"])
        layout.addWidget(self.label)
        
    def show_message(self, text, duration=2000, message_type='default'):
        # Комбинируем базовый стиль со стилем для конкретного типа сообщения
        style = THEMES[self.theme]["OVERLAY_MESSAGE_STYLES"][message_type]
        
        self.label.setStyleSheet(style)
        self.label.setText(text)
        self.adjustSize()
        
        # Получаем главное окно приложения
        main_window = QApplication.instance().activeWindow()
        if main_window:
            # Позиционируем сообщение внизу по центру главного окна
            main_rect = main_window.rect()
            x = main_window.x() + (main_rect.width() - self.width()) // 2
            y = main_window.y() + main_rect.height() - self.height() - 30  # 30 пикселей отступ снизу
            self.move(x, y)
        
        self.show()
        if duration > 0:
            QTimer.singleShot(duration, self.hide)
        
    def show_error(self, text, duration=3000):
        self.show_message(text, duration, 'error')
        
    def show_warning(self, text, duration=2500):
        self.show_message(text, duration, 'warning')
        
    def show_success(self, text, duration=2000):
        self.show_message(text, duration, 'success')
        
    def mousePressEvent(self, event):
        self.hide()
        
    def resizeEvent(self, event):
        """Обновляем позицию при изменении размера окна"""
        super().resizeEvent(event)
        if self.isVisible():
            main_window = QApplication.instance().activeWindow()
            if main_window:
                main_rect = main_window.rect()
                x = main_window.x() + (main_rect.width() - self.width()) // 2
                y = main_window.y() + main_rect.height() - self.height() - 30
                self.move(x, y) 