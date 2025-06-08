from PyQt6.QtCore import QTimer, QObject, pyqtSignal
from datetime import datetime


class AutoLock(QObject):
    lock_triggered = pyqtSignal()  # Сигнал для блокировки приложения

    def __init__(self, timeout_seconds=300):
        super().__init__()
        self.timeout_seconds = timeout_seconds
        self.last_activity = datetime.now()
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_inactivity)
        self.start_monitoring()

    def start_monitoring(self):
        """Запуск мониторинга активности"""
        self.timer.start(1000)  # Проверка каждую секунду

    def stop_monitoring(self):
        """Остановка мониторинга активности"""
        self.timer.stop()

    def activity_detected(self):
        """Вызывается при обнаружении активности пользователя"""
        self.last_activity = datetime.now()

    def check_inactivity(self):
        """Проверка времени неактивности"""
        inactive_time = (datetime.now() - self.last_activity).total_seconds()
        if inactive_time >= self.timeout_seconds:
            self.lock_triggered.emit()
            self.stop_monitoring()

    def set_timeout(self, seconds):
        """Установка нового времени ожидания"""
        self.timeout_seconds = seconds 