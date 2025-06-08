import os
import json
import time
from typing import Optional, Dict, List, Any
from .crypto_manager import CryptoManagerV2
from .backup_manager import BackupManager
from .validators import DataValidator


class PasswordManager:
    """Основной класс для работы с паролями"""
    VAULT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "vaults")

    def __init__(self, login: str, password: str):
        """Инициализация менеджера паролей"""
        self.login = login
        self.vault_path = self._get_vault_path(login)
        self.crypto = CryptoManagerV2(login, password)
        self.backup = BackupManager(self.crypto)
        self.validator = DataValidator()
        self.data = {"passwords": [], "categories": ["Без категории"]}
        self._ensure_vault_dir_exists()
        self._load_data()

    @property
    def passwords(self) -> list:
        """Возвращает список паролей"""
        return self.data.get("passwords", []).copy()  # Возвращаем копию для безопасности

    @classmethod
    def _get_vault_path(cls, login: str) -> str:
        """Получает путь к хранилищу пользователя"""
        return os.path.join(cls.VAULT_DIR, f"{login}.vault")

    @classmethod
    def vault_exists(cls, login: str) -> bool:
        """Проверяет существование хранилища"""
        return os.path.exists(cls._get_vault_path(login))

    def _ensure_vault_dir_exists(self):
        """Создает директорию для хранилища если она не существует"""
        if not os.path.exists(self.VAULT_DIR):
            os.makedirs(self.VAULT_DIR, mode=0o700)

    def _load_data(self):
        """Загружает данные из хранилища"""
        try:
            if os.path.exists(self.vault_path):
                with open(self.vault_path, 'r') as f:
                    content = f.read()
                    if content:
                        self.data = self.crypto.decrypt_data(content)
                    else:
                        self.data = {"passwords": [], "categories": ["Без категории"]}
        except Exception as e:
            print(f"Ошибка загрузки данных: {str(e)}")
            self.data = {"passwords": [], "categories": ["Без категории"]}

    def save_data(self) -> bool:
        """Сохраняет данные в хранилище"""
        try:
            # Создаем бэкап перед сохранением
            self.backup.create_backup(self.vault_path, self.data)
            
            # Шифруем и сохраняем данные
            encrypted = self.crypto.encrypt_data(self.data)
            with open(self.vault_path, 'w') as f:
                f.write(encrypted)
                
            return True
        except Exception as e:
            print(f"Ошибка сохранения данных: {str(e)}")
            return False

    def save_password(self, service: str, password: str, category: str = "Без категории", **kwargs) -> bool:
        """Сохраняет новый пароль или обновляет существующий"""
        try:
            # Валидация данных
            if not self.validator.validate_service(service):
                raise ValueError("Некорректное название сервиса")
            if not self.validator.validate_password(password):
                raise ValueError("Некорректный пароль")
            if not self.validator.validate_category(category):
                raise ValueError("Некорректная категория")

            # Проверяем дополнительные поля
            for key, value in kwargs.items():
                if key == "url" and not self.validator.validate_url(value):
                    raise ValueError("Некорректный URL")
                elif key == "email" and not self.validator.validate_email(value):
                    raise ValueError("Некорректный email")
                elif key == "phone" and not self.validator.validate_phone(value):
                    raise ValueError("Некорректный телефон")
                elif key == "notes" and not self.validator.validate_notes(value):
                    raise ValueError("Слишком длинные заметки")

            # Создаем или обновляем запись
            entry = {
                "service": service,
                "password": password,
                "category": category,
                "created": int(time.time()),
                "modified": int(time.time())
            }
            entry.update(kwargs)  # Добавляем дополнительные поля

            # Ищем существующую запись
            existing_index = None
            for i, item in enumerate(self.data["passwords"]):
                if item["service"] == service:
                    existing_index = i
                    break

            if existing_index is not None:
                # Обновляем существующую запись
                old_entry = self.data["passwords"][existing_index]
                entry["created"] = old_entry.get("created", entry["created"])
                self.data["passwords"][existing_index] = entry
            else:
                # Добавляем новую запись
                self.data["passwords"].append(entry)

            # Добавляем категорию, если её нет
            if category not in self.data["categories"]:
                self.data["categories"].append(category)

            return self.save_data()

        except Exception as e:
            print(f"Ошибка сохранения пароля: {str(e)}")
            return False

    def get_entry_by_service(self, service_name: str) -> Optional[dict]:
        """Получает запись по названию сервиса"""
        try:
            for entry in self.data["passwords"]:
                if entry["service"] == service_name:
                    return entry.copy()  # Возвращаем копию для безопасности
            return None
        except Exception as e:
            print(f"Ошибка получения записи: {str(e)}")
            return None

    def filter_entries(self, search_text: str = "", category: str = "Все категории") -> List[Dict[str, Any]]:
        """Фильтрует записи по тексту поиска и категории"""
        try:
            filtered = []
            search_text = search_text.lower()

            for entry in self.data["passwords"]:
                # Фильтр по категории
                if category != "Все категории" and entry["category"] != category:
                    continue

                # Фильтр по тексту
                if search_text:
                    service = entry["service"].lower()
                    url = entry.get("url", "").lower()
                    email = entry.get("email", "").lower()
                    notes = entry.get("notes", "").lower()

                    if not any([
                        search_text in service,
                        search_text in url,
                        search_text in email,
                        search_text in notes
                    ]):
                        continue

                filtered.append(entry.copy())  # Добавляем копию для безопасности

            return filtered

        except Exception as e:
            print(f"Ошибка фильтрации записей: {str(e)}")
            return []

    def add_category(self, name: str) -> bool:
        """Добавляет новую категорию"""
        try:
            if not self.validator.validate_category(name):
                raise ValueError("Некорректное название категории")

            if name not in self.data["categories"]:
                self.data["categories"].append(name)
                return self.save_data()
            return True

        except Exception as e:
            print(f"Ошибка добавления категории: {str(e)}")
            return False

    def change_password(self, new_password: str) -> bool:
        """Меняет мастер-пароль"""
        try:
            # Создаем новый крипто-менеджер
            new_crypto = CryptoManagerV2(self.login, new_password)
            
            # Создаем бэкап перед изменением
            self.backup.create_backup(self.vault_path, self.data)
            
            # Пробуем зашифровать данные новым паролем
            encrypted = new_crypto.encrypt_data(self.data)
            
            # Проверяем, что можем расшифровать
            test_decrypt = new_crypto.decrypt_data(encrypted)
            if test_decrypt != self.data:
                raise ValueError("Ошибка проверки нового пароля")
            
            # Сохраняем зашифрованные данные
            with open(self.vault_path, 'w') as f:
                f.write(encrypted)
            
            # Обновляем текущий крипто-менеджер
            self.crypto = new_crypto
            return True

        except Exception as e:
            print(f"Ошибка смены пароля: {str(e)}")
            return False

    def change_username(self, new_username: str) -> bool:
        """Меняет имя пользователя"""
        try:
            if not new_username or len(new_username) > 100:
                raise ValueError("Некорректное имя пользователя")

            new_vault_path = self._get_vault_path(new_username)
            if os.path.exists(new_vault_path):
                raise ValueError("Пользователь с таким именем уже существует")

            # Создаем новый крипто-менеджер
            new_crypto = CryptoManagerV2(new_username, self.crypto.combined_secret.decode().split("::")[-1])
            
            # Создаем бэкап перед изменением
            self.backup.create_backup(self.vault_path, self.data)
            
            # Шифруем данные с новым именем пользователя
            encrypted = new_crypto.encrypt_data(self.data)
            
            # Сохраняем в новый файл
            with open(new_vault_path, 'w') as f:
                f.write(encrypted)
            
            # Удаляем старый файл
            try:
                os.remove(self.vault_path)
            except:
                pass  # Игнорируем ошибки удаления
            
            # Обновляем текущее состояние
            self.login = new_username
            self.vault_path = new_vault_path
            self.crypto = new_crypto
            return True

        except Exception as e:
            print(f"Ошибка смены имени пользователя: {str(e)}")
            return False

    def add_entry(self, data: dict) -> bool:
        """Добавляет новую запись"""
        try:
            required_fields = ["service", "password"]
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Отсутствует обязательное поле: {field}")

            return self.save_password(
                service=data["service"],
                password=data["password"],
                category=data.get("category", "Без категории"),
                **{k: v for k, v in data.items() if k not in ["service", "password", "category"]}
            )

        except Exception as e:
            print(f"Ошибка добавления записи: {str(e)}")
            return False

    def clear_sensitive_data(self):
        """Очищает конфиденциальные данные из памяти"""
        try:
            # Очищаем данные
            self.data = {"passwords": [], "categories": ["Без категории"]}
            
            # Очищаем криптографические ключи
            if hasattr(self, 'crypto'):
                self.crypto.combined_secret = b""
            
            # Принудительно вызываем сборщик мусора
            import gc
            gc.collect()
            
        except Exception as e:
            print(f"Ошибка при очистке конфиденциальных данных: {str(e)}") 