import hashlib
import requests
from typing import Dict, Optional
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
import time
import queue
from threading import Thread, Lock, Event

class HIBPChecker(QObject):
    status_ready = pyqtSignal(dict)  # Сигнал с результатом проверки
    MAX_CACHE_SIZE = 1000
    CHECK_DELAY = 300  # мс
    REQUEST_TIMEOUT = 2  # секунды
    MIN_REQUEST_INTERVAL = 1.5  # секунды

    def __init__(self):
        super().__init__()
        self._check_timer = QTimer()
        self._check_timer.setSingleShot(True)
        self._check_timer.timeout.connect(self._delayed_check)
        self._current_password: Optional[str] = None
        self._cache = {}
        self._cache_lock = Lock()
        self._last_request_time = 0
        self._request_lock = Lock()
        self._request_queue = queue.Queue()
        self._stop_event = Event()
        
        # Запускаем поток обработки
        self._worker_thread = Thread(target=self._process_requests, daemon=True)
        self._worker_thread.start()

    def check_password(self, password: str):
        """Запускает проверку пароля"""
        # Немедленная проверка на пустой пароль
        if not password:
            self.status_ready.emit({'severity': 'empty'})
            return

        # Проверка кэша
        with self._cache_lock:
            if password in self._cache:
                self.status_ready.emit(self._cache[password])
                return

        # Отмена предыдущей отложенной проверки
        self._check_timer.stop()
        self._current_password = password
        self._check_timer.start(self.CHECK_DELAY)

    def _delayed_check(self):
        """Отложенная проверка пароля"""
        if not self._current_password:
            return

        try:
            # Добавляем запрос в очередь
            self._request_queue.put(self._current_password, timeout=1)
        except queue.Full:
            # Если очередь переполнена, пропускаем запрос
            pass

    def _process_requests(self):
        """Обработка запросов в отдельном потоке"""
        while not self._stop_event.is_set():
            try:
                # Ждем новый пароль не более 0.5 секунд
                password = self._request_queue.get(timeout=0.5)
                
                # Пропускаем, если это не текущий пароль
                if password != self._current_password:
                    continue

                # Получаем статус пароля
                try:
                    status = self._get_password_status(password)
                    
                    # Кэшируем результат
                    with self._cache_lock:
                        self._cache[password] = status
                        # Очистка кэша при превышении размера
                        while len(self._cache) > self.MAX_CACHE_SIZE:
                            self._cache.pop(next(iter(self._cache)))

                    # Отправляем результат только если это все еще текущий пароль
                    if password == self._current_password:
                        self.status_ready.emit(status)
                        
                except Exception as e:
                    # В случае ошибки отправляем статус офлайн-проверки
                    if password == self._current_password:
                        offline_status = self._get_offline_status(password)
                        self.status_ready.emit(offline_status)

            except queue.Empty:
                # Таймаут очереди - это нормально
                continue
            except Exception:
                # Любые другие ошибки не должны прерывать поток
                continue

    def _get_offline_status(self, password: str) -> dict:
        """Проверяет пароль локально без обращения к API"""
        if not password:
            return {'severity': 'empty'}

        # Проверка сложности
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)
        strength_score = sum([has_upper, has_lower, has_digit, has_special])

        if len(password) < 8:
            return {
                'status': 'Too Short',
                'message': 'Password is too short',
                'severity': 'danger'
            }
        elif strength_score < 3:
            return {
                'status': 'Weak',
                'message': 'Password is too weak',
                'severity': 'danger'
            }
        elif strength_score >= 3 and len(password) >= 12:
            return {
                'status': 'Potentially Safe',
                'message': 'Strong password (offline check)',
                'severity': 'safe'
            }
        else:
            return {
                'status': 'Moderate',
                'message': 'Password strength is moderate',
                'severity': 'warning'
            }

    def _get_password_status(self, password: str) -> dict:
        """Проверяет безопасность пароля через API"""
        # Сначала делаем офлайн проверку
        offline_status = self._get_offline_status(password)
        if offline_status['severity'] == 'danger':
            return offline_status

        try:
            # Получаем хэш пароля
            password_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
            prefix, suffix = password_hash[:5], password_hash[5:].lower()
            
            # Проверяем интервал между запросами
            with self._request_lock:
                current_time = time.time()
                time_since_last_request = current_time - self._last_request_time
                if time_since_last_request < self.MIN_REQUEST_INTERVAL:
                    time.sleep(self.MIN_REQUEST_INTERVAL - time_since_last_request)

                # Делаем запрос
                response = requests.get(
                    f"https://api.pwnedpasswords.com/range/{prefix}",
                    timeout=self.REQUEST_TIMEOUT
                )
                response.raise_for_status()
                self._last_request_time = time.time()

            # Проверяем наличие пароля в базе
            for line in response.text.splitlines():
                if line.lower().startswith(suffix):
                    count = int(line.split(':')[1])
                    if count > 10:
                        return {
                            'status': 'Compromised',
                            'message': f'Found in {count} data breaches',
                            'severity': 'danger'
                        }
                    elif count > 0:
                        return {
                            'status': 'Warning',
                            'message': f'Found in {count} data breaches',
                            'severity': 'warning'
                        }

            # Если пароль не найден в базе и достаточно сложный
            return {
                'status': 'Safe',
                'message': 'Strong and unique password',
                'severity': 'safe'
            }

        except Exception:
            # В случае ошибки возвращаем результат офлайн проверки
            return offline_status

    def cleanup(self):
        """Очистка ресурсов при закрытии"""
        self._stop_event.set()  # Сигнал потоку о завершении
        if self._worker_thread.is_alive():
            try:
                # Добавляем пустой элемент в очередь, чтобы разблокировать поток
                self._request_queue.put(None, timeout=0.1)
            except queue.Full:
                pass
            # Ждем завершения потока не более 1 секунды
            self._worker_thread.join(timeout=1.0) 