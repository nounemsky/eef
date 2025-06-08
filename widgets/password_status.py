from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from styles import PASSWORD_STATUS_WIDGET_STYLES

class PasswordStatusWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        self.status_label = QLabel()
        self.status_label.setStyleSheet(PASSWORD_STATUS_WIDGET_STYLES['base'])
        
        layout.addWidget(self.status_label)
        self.setLayout(layout)
        self.hide()
        
    def update_status(self, status_data: dict):
        """Обновляет статус пароля"""
        if not status_data or not isinstance(status_data, dict):
            self.hide()
            return
            
        severity = status_data.get('severity')
        if not severity or severity == 'empty':
            self.hide()
            return
            
        status_text = {
            'safe': "✓ Надежный",
            'warning': "⚠ Средний",
            'danger': "✗ Слабый"
        }.get(severity, "")
        
        if not status_text:
            self.hide()
            return
            
        self.status_label.setText(status_text)
        self.status_label.setStyleSheet(
            PASSWORD_STATUS_WIDGET_STYLES['base'] + 
            PASSWORD_STATUS_WIDGET_STYLES.get(severity, PASSWORD_STATUS_WIDGET_STYLES['safe'])
        )
        self.show() 