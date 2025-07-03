import os
import json
import time
import logging
from typing import Optional, Dict, List, Any
from .crypto_manager import CryptoManagerV2
from .backup_manager import BackupManager
from .validators import DataValidator


class PasswordManager:
    """Основной класс для работы с паролями"""
    VAULT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "vaults")

    def __init__(self, login: str, password: str):
        """Инициализация менеджера паролей"""
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Инициализация PasswordManager для пользователя {login}")
        
        self.login = login
        self.vault_path = self._get_vault_path(login)
        self.logger.debug(f"Путь к vault файлу: {self.vault_path}")
        
        self.crypto = CryptoManagerV2(login, password)
        self.backup = BackupManager(self.crypto)
        self.validator = DataValidator()
        self.data = {"passwords": [], "categories": ["Без категории"]}
        
        try:
            self._ensure_vault_dir_exists()
            self._load_data()
        except Exception as e:
            self.logger.error(f"Ошибка инициализации: {str(e)}", exc_info=True)
            raise

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
        try:
            # Создаем все необходимые директории
            dirs_to_check = [
                self.VAULT_DIR,
                os.path.join(os.path.dirname(os.path.dirname(__file__)), "backups"),
                os.path.join(os.path.dirname(os.path.dirname(__file__)), "app_cache")
            ]
            
            for dir_path in dirs_to_check:
                self.logger.debug(f"Проверка директории: {dir_path}")
                if not os.path.exists(dir_path):
                    self.logger.info(f"Создание директории: {dir_path}")
                    os.makedirs(dir_path, exist_ok=True)
                
                # Проверяем права на запись
                test_file = os.path.join(dir_path, '.test')
                try:
                    self.logger.debug(f"Проверка прав на запись в {dir_path}")
                    with open(test_file, 'w') as f:
                        f.write('test')
                    os.remove(test_file)
                    self.logger.debug(f"Права на запись в {dir_path} подтверждены")
                except Exception as e:
                    self.logger.error(f"Нет прав на запись в директорию {dir_path}: {str(e)}")
                    raise ValueError(f"Нет прав на запись в директорию {dir_path}: {str(e)}")
                    
            # Проверяем права на vault файл
            if os.path.exists(self.vault_path):
                try:
                    self.logger.debug(f"Проверка прав на vault файл: {self.vault_path}")
                    with open(self.vault_path, 'a') as f:
                        pass
                    self.logger.debug("Права на vault файл подтверждены")
                except Exception as e:
                    self.logger.error(f"Нет прав на запись в файл vault: {str(e)}")
                    raise ValueError(f"Нет прав на запись в файл vault: {str(e)}")
                    
        except Exception as e:
            self.logger.error(f"Ошибка проверки директорий: {str(e)}", exc_info=True)
            raise

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
        temp_path = None
        try:
            self.logger.info("Начало процесса сохранения данных")
            
            # Проверяем права доступа перед сохранением
            if os.path.exists(self.vault_path):
                try:
                    self.logger.debug(f"Проверка блокировки файла: {self.vault_path}")
                    with open(self.vault_path, 'r+') as f:
                        # Получаем эксклюзивную блокировку
                        import msvcrt
                        self.logger.debug("Попытка получить блокировку файла")
                        msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                        # Освобождаем блокировку
                        msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
                        self.logger.debug("Блокировка файла успешно проверена")
                except Exception as e:
                    self.logger.error(f"Файл vault заблокирован или недоступен: {str(e)}")
                    raise ValueError(f"Файл vault заблокирован или недоступен: {str(e)}")
            
            # Создаем временный файл в той же директории
            temp_path = os.path.join(os.path.dirname(self.vault_path), f".tmp_{os.path.basename(self.vault_path)}")
            self.logger.debug(f"Создание временного файла: {temp_path}")
            
            # Шифруем данные
            self.logger.debug("Шифрование данных")
            encrypted = self.crypto.encrypt_data(self.data)
            
            # Записываем во временный файл
            self.logger.debug("Запись во временный файл")
            with open(temp_path, 'w') as f:
                f.write(encrypted)
            
            # Создаем бэкап только после успешной записи во временный файл
            self.logger.debug("Создание резервной копии")
            backup_result = self.backup.create_backup(self.vault_path, self.data)
            if not backup_result:
                self.logger.error("Не удалось создать резервную копию")
                raise ValueError("Не удалось создать резервную копию")
            
            # Если файл vault существует, пытаемся его удалить
            if os.path.exists(self.vault_path):
                try:
                    self.logger.debug(f"Удаление старого файла: {self.vault_path}")
                    os.remove(self.vault_path)
                except Exception as e:
                    self.logger.warning(f"Не удалось удалить старый файл: {str(e)}")
                    # Ждем немного и пробуем снова
                    import time
                    time.sleep(0.1)
                    self.logger.debug("Повторная попытка удаления старого файла")
                    os.remove(self.vault_path)
            
            # Переименовываем временный файл
            self.logger.debug(f"Переименование временного файла {temp_path} в {self.vault_path}")
            os.rename(temp_path, self.vault_path)
            
            self.logger.info("Данные успешно сохранены")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка сохранения данных: {str(e)}", exc_info=True)
            # Очищаем временный файл при ошибке
            if temp_path and os.path.exists(temp_path):
                try:
                    self.logger.debug(f"Удаление временного файла после ошибки: {temp_path}")
                    os.remove(temp_path)
                except:
                    self.logger.warning(f"Не удалось удалить временный файл: {temp_path}")
            return False

    def save_password(self, service: str, password: str, category: str = "Без категории", **kwargs) -> bool:
        """Сохраняет новый пароль или обновляет существующий"""
        try:
            self.logger.info(f"Попытка сохранения пароля для сервиса: {service}")
            
            # Валидация данных
            self.logger.debug("Валидация данных")
            if not self.validator.validate_service(service):
                raise ValueError("Некорректное название сервиса")
            if not self.validator.validate_password(password):
                raise ValueError("Некорректный пароль")
            if not self.validator.validate_category(category):
                raise ValueError("Некорректная категория")

            # Проверяем дополнительные поля
            for key, value in kwargs.items():
                self.logger.debug(f"Проверка дополнительного поля: {key}")
                if key == "url" and not self.validator.validate_url(value):
                    raise ValueError("Некорректный URL")
                elif key == "email" and not self.validator.validate_email(value):
                    raise ValueError("Некорректный email")

            # Добавляем timestamp
            current_time = int(time.time())
            
            # Ищем существующую запись
            for entry in self.data["passwords"]:
                if entry["service"] == service:
                    # Обновляем существующую запись
                    entry.update({
                        "password": password,
                        "category": category,
                        "modified_at": current_time,
                        **kwargs
                    })
                    break
            else:
                # Создаем новую запись
                new_entry = {
                    "service": service,
                    "password": password,
                    "category": category,
                    "created_at": current_time,
                    "modified_at": current_time,
                    **kwargs
                }
                self.data["passwords"].append(new_entry)

            # Добавляем категорию, если её нет
            if category not in self.data["categories"]:
                self.data["categories"].append(category)

            return self.save_data()

        except Exception as e:
            self.logger.error(f"Ошибка сохранения пароля: {str(e)}", exc_info=True)
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
            
            self.logger.debug(f"Начало фильтрации. Всего паролей: {len(self.data['passwords'])}")
            self.logger.debug(f"Поисковый запрос: '{search_text}', категория: '{category}'")

            for i, entry in enumerate(self.data["passwords"]):
                try:
                    # Проверяем структуру записи
                    if not isinstance(entry, dict):
                        self.logger.error(f"Некорректный тип записи #{i}: {type(entry)}")
                        continue
                        
                    # Проверяем обязательные поля
                    required_fields = ["service", "password", "category"]
                    missing_fields = [field for field in required_fields if field not in entry]
                    if missing_fields:
                        self.logger.error(f"В записи #{i} отсутствуют обязательные поля: {missing_fields}")
                        continue

                    # Фильтр по категории
                    if category != "Все категории" and entry["category"] != category:
                        self.logger.debug(f"Запись #{i} пропущена по категории")
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
                            self.logger.debug(f"Запись #{i} не соответствует поисковому запросу")
                            continue

                    self.logger.debug(f"Добавляем запись #{i} (сервис: {entry.get('service', 'unknown')})")
                    filtered.append(entry.copy())  # Добавляем копию для безопасности
                    
                except Exception as e:
                    self.logger.error(f"Ошибка при обработке записи #{i}: {str(e)}", exc_info=True)
                    continue

            self.logger.debug(f"Фильтрация завершена. Найдено записей: {len(filtered)}")
            return filtered

        except Exception as e:
            self.logger.error(f"Ошибка фильтрации записей: {str(e)}", exc_info=True)
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