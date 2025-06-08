import time
from typing import Dict, Optional, List
import json
import os
from threading import Lock

class BruteForceProtection:
    """Класс для защиты от брутфорс-атак"""
    
    def __init__(self, max_attempts: int = 5, lockout_time: int = 300):
        print(f"Инициализация BruteForceProtection (max_attempts={max_attempts}, lockout_time={lockout_time})")
        self.max_attempts = max_attempts  # Максимальное количество попыток
        self.lockout_time = lockout_time  # Время блокировки в секундах
        self.attempts: Dict[str, Dict] = {}  # Словарь для хранения попыток
        self._lock = Lock()  # Для потокобезопасности
        self.storage_file = "auth_attempts.json"
        self._load_attempts()
    
    def _load_attempts(self):
        """Загружает историю попыток из файла"""
        try:
            if os.path.exists(self.storage_file):
                print(f"Загрузка данных из {self.storage_file}")
                with open(self.storage_file, 'r') as f:
                    try:
                        data = json.load(f)
                        # Преобразуем списки IP-адресов обратно в множества
                        self.attempts = {}
                        for username, info in data.items():
                            self.attempts[username] = {
                                "count": int(info.get("count", 0)),
                                "last_attempt": float(info.get("last_attempt", 0)),
                                "ip_addresses": set(info.get("ip_addresses", []))
                            }
                        print(f"Загружено {len(self.attempts)} записей")
                    except json.JSONDecodeError as e:
                        print(f"Ошибка декодирования JSON: {str(e)}")
                        self.attempts = {}
                # Очищаем устаревшие записи при загрузке
                self._cleanup_old_attempts()
        except Exception as e:
            print(f"Ошибка загрузки попыток входа: {str(e)}")
            self.attempts = {}
    
    def _save_attempts(self):
        """Сохраняет историю попыток в файл"""
        try:
            print(f"Сохранение данных в {self.storage_file}")
            # Преобразуем множества IP-адресов в списки для JSON
            data = {}
            for username, info in self.attempts.items():
                data[username] = {
                    "count": info["count"],
                    "last_attempt": info["last_attempt"],
                    "ip_addresses": list(info["ip_addresses"])
                }
            
            # Сначала сохраняем во временный файл
            temp_file = f"{self.storage_file}.tmp"
            with open(temp_file, 'w') as f:
                json.dump(data, f)
            
            # Если сохранение прошло успешно, заменяем основной файл
            os.replace(temp_file, self.storage_file)
            print("Данные успешно сохранены")
        except Exception as e:
            print(f"Ошибка сохранения попыток входа: {str(e)}")
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
    
    def _cleanup_old_attempts(self):
        """Очищает устаревшие записи о попытках"""
        current_time = time.time()
        cleaned = 0
        with self._lock:
            for username in list(self.attempts.keys()):
                if current_time - self.attempts[username]["last_attempt"] > self.lockout_time:
                    del self.attempts[username]
                    cleaned += 1
        if cleaned > 0:
            print(f"Очищено {cleaned} устаревших записей")
            self._save_attempts()  # Сохраняем изменения
    
    def check_attempt(self, username: str, ip_address: Optional[str] = None) -> tuple[bool, int, int]:
        """
        Проверяет, можно ли совершить попытку входа
        
        Args:
            username: имя пользователя
            ip_address: IP-адрес (опционально)
            
        Returns:
            tuple[bool, int, int]: (можно_ли_попытаться, осталось_попыток, время_до_разблокировки)
        """
        current_time = time.time()
        
        with self._lock:
            # Очищаем старые записи
            self._cleanup_old_attempts()
            
            # Получаем информацию о попытках для пользователя
            user_attempts = self.attempts.get(username, {
                "count": 0,
                "last_attempt": 0,
                "ip_addresses": set()
            })
            
            # Проверяем, не заблокирован ли пользователь
            if user_attempts["count"] >= self.max_attempts:
                time_passed = current_time - user_attempts["last_attempt"]
                if time_passed < self.lockout_time:
                    remaining = int(self.lockout_time - time_passed)
                    print(f"Пользователь {username} заблокирован на {remaining} секунд")
                    return False, 0, remaining
                else:
                    # Сбрасываем счетчик после истечения времени блокировки
                    print(f"Сброс счетчика попыток для пользователя {username}")
                    user_attempts["count"] = 0
                    user_attempts["ip_addresses"] = set()
                    self.attempts[username] = user_attempts
                    self._save_attempts()
            
            remaining_attempts = self.max_attempts - user_attempts["count"]
            print(f"Пользователь {username}: осталось попыток {remaining_attempts}")
            return True, remaining_attempts, 0
    
    def record_attempt(self, username: str, success: bool, ip_address: Optional[str] = None):
        """
        Записывает попытку входа
        
        Args:
            username: имя пользователя
            success: успешная ли попытка
            ip_address: IP-адрес (опционально)
        """
        current_time = time.time()
        
        with self._lock:
            if username not in self.attempts:
                self.attempts[username] = {
                    "count": 0,
                    "last_attempt": current_time,
                    "ip_addresses": set()
                }
            
            if not success:
                self.attempts[username]["count"] += 1
                if ip_address:
                    self.attempts[username]["ip_addresses"].add(ip_address)
                print(f"Неудачная попытка для {username} (попытка #{self.attempts[username]['count']})")
            else:
                # При успешном входе сбрасываем счетчик
                print(f"Успешный вход для {username}, сброс счетчика")
                self.attempts[username]["count"] = 0
                self.attempts[username]["ip_addresses"] = set()
            
            self.attempts[username]["last_attempt"] = current_time
            self._save_attempts()
    
    def get_status(self, username: str) -> dict:
        """Возвращает текущий статус попыток входа для пользователя"""
        with self._lock:
            if username not in self.attempts:
                return {
                    "attempts": 0,
                    "is_locked": False,
                    "remaining_time": 0,
                    "remaining_attempts": self.max_attempts
                }
            
            user_attempts = self.attempts[username]
            current_time = time.time()
            time_passed = current_time - user_attempts["last_attempt"]
            
            is_locked = (user_attempts["count"] >= self.max_attempts and 
                        time_passed < self.lockout_time)
            
            status = {
                "attempts": user_attempts["count"],
                "is_locked": is_locked,
                "remaining_time": int(self.lockout_time - time_passed) if is_locked else 0,
                "remaining_attempts": max(0, self.max_attempts - user_attempts["count"])
            }
            print(f"Статус для {username}: {status}")
            return status 