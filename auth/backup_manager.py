import os
import time
import shutil
import logging
from .crypto_manager import CryptoManagerV2


class BackupManager:
    BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backups")
    MAX_BACKUPS = 5  # Максимальное количество резервных копий

    def __init__(self, crypto_manager: CryptoManagerV2):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Инициализация BackupManager")
        self.crypto = crypto_manager
        self._ensure_backup_dir_exists()

    def _ensure_backup_dir_exists(self):
        """Создает и проверяет директорию для бэкапов"""
        try:
            self.logger.debug(f"Проверка директории бэкапов: {self.BACKUP_DIR}")
            if not os.path.exists(self.BACKUP_DIR):
                self.logger.info(f"Создание директории бэкапов: {self.BACKUP_DIR}")
                os.makedirs(self.BACKUP_DIR, exist_ok=True)
            
            # Проверяем права на запись
            test_file = os.path.join(self.BACKUP_DIR, '.test')
            try:
                self.logger.debug("Проверка прав на запись")
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                self.logger.debug("Права на запись подтверждены")
            except Exception as e:
                self.logger.error(f"Нет прав на запись в директорию бэкапов: {str(e)}")
                raise ValueError(f"Нет прав на запись в директорию бэкапов: {str(e)}")
                
        except Exception as e:
            self.logger.error(f"Ошибка при работе с директорией бэкапов: {str(e)}", exc_info=True)
            raise

    def _get_backup_path(self, original_path: str, timestamp: int = None) -> str:
        """Получает путь для бэкапа"""
        base_name = os.path.basename(original_path)
        name, ext = os.path.splitext(base_name)
        timestamp = timestamp or int(time.time())
        backup_path = os.path.join(self.BACKUP_DIR, f"{name}_backup_{timestamp}{ext}")
        self.logger.debug(f"Сгенерирован путь для бэкапа: {backup_path}")
        return backup_path

    def create_backup(self, file_path: str, data: dict) -> bool:
        """Создает зашифрованную резервную копию"""
        temp_path = None
        try:
            self.logger.info(f"Создание резервной копии для файла: {file_path}")
            
            # Проверяем доступность директории
            self._ensure_backup_dir_exists()
            
            # Шифруем данные с дополнительной солью для бэкапа
            self.logger.debug("Подготовка данных для бэкапа")
            backup_data = {
                "data": data,
                "original_path": file_path,
                "timestamp": int(time.time())
            }
            
            self.logger.debug("Шифрование данных")
            encrypted = self.crypto.encrypt_data(backup_data)
            
            # Сначала пишем во временный файл
            backup_path = self._get_backup_path(file_path)
            temp_path = f"{backup_path}.tmp"
            
            self.logger.debug(f"Запись во временный файл: {temp_path}")
            with open(temp_path, "w") as f:
                f.write(encrypted)
            
            # Проверяем, что данные записались корректно
            self.logger.debug("Проверка записанных данных")
            with open(temp_path, "r") as f:
                content = f.read()
                if content != encrypted:
                    self.logger.error("Ошибка проверки записанных данных")
                    raise ValueError("Ошибка проверки записанных данных")
            
            # Перемещаем временный файл
            if os.path.exists(backup_path):
                self.logger.debug(f"Удаление существующего бэкапа: {backup_path}")
                os.remove(backup_path)
            
            self.logger.debug(f"Переименование временного файла {temp_path} в {backup_path}")
            os.rename(temp_path, backup_path)
            
            # Проверяем и удаляем старые бэкапы
            self.logger.debug("Очистка старых бэкапов")
            self._cleanup_old_backups(file_path)
            
            self.logger.info("Резервная копия успешно создана")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка создания бэкапа: {str(e)}", exc_info=True)
            if temp_path and os.path.exists(temp_path):
                try:
                    self.logger.debug(f"Удаление временного файла после ошибки: {temp_path}")
                    os.remove(temp_path)
                except:
                    self.logger.warning(f"Не удалось удалить временный файл: {temp_path}")
            return False

    def restore_from_backup(self, original_path: str, timestamp: int = None) -> dict | None:
        """Восстанавливает данные из бэкапа"""
        try:
            self.logger.info(f"Попытка восстановления из бэкапа для файла: {original_path}")
            
            # Находим нужный бэкап
            backup_path = self._get_backup_path(original_path, timestamp)
            if not os.path.exists(backup_path):
                self.logger.warning(f"Файл бэкапа не найден: {backup_path}")
                return None

            # Расшифровываем и проверяем данные
            self.logger.debug(f"Чтение файла бэкапа: {backup_path}")
            with open(backup_path, "r") as f:
                content = f.read()
                
            self.logger.debug("Расшифровка данных")
            decrypted = self.crypto.decrypt_data(content)
            if not isinstance(decrypted, dict) or "data" not in decrypted:
                self.logger.error("Поврежденный файл бэкапа")
                raise ValueError("Поврежденный файл бэкапа")
                
            if decrypted.get("original_path") != original_path:
                self.logger.error("Несоответствие пути файла в бэкапе")
                raise ValueError("Несоответствие пути файла!")
                
            self.logger.info("Данные успешно восстановлены из бэкапа")
            return decrypted.get("data")
            
        except Exception as e:
            self.logger.error(f"Ошибка восстановления из бэкапа: {str(e)}", exc_info=True)
            return None

    def _cleanup_old_backups(self, original_path: str):
        """Удаляет старые резервные копии, оставляя только MAX_BACKUPS последних"""
        try:
            self.logger.debug(f"Начало очистки старых бэкапов для файла: {original_path}")
            
            base_name = os.path.basename(original_path)
            name, ext = os.path.splitext(base_name)
            pattern = f"{name}_backup_*{ext}"
            
            # Получаем список всех бэкапов для данного файла
            backups = []
            for filename in os.listdir(self.BACKUP_DIR):
                if filename.startswith(f"{name}_backup_") and filename.endswith(ext):
                    full_path = os.path.join(self.BACKUP_DIR, filename)
                    try:
                        mtime = os.path.getmtime(full_path)
                        backups.append((mtime, full_path))
                        self.logger.debug(f"Найден бэкап: {full_path}")
                    except:
                        self.logger.warning(f"Не удалось получить время модификации файла: {full_path}")
                        continue
            
            # Сортируем по времени создания (новые в конце)
            backups.sort()
            
            # Удаляем старые бэкапы
            while len(backups) > self.MAX_BACKUPS:
                _, path = backups.pop(0)
                try:
                    if os.path.exists(path):
                        self.logger.debug(f"Удаление старого бэкапа: {path}")
                        os.remove(path)
                except Exception as e:
                    self.logger.error(f"Не удалось удалить старый бэкап {path}: {str(e)}")
                    
        except Exception as e:
            self.logger.error(f"Ошибка при очистке старых бэкапов: {str(e)}", exc_info=True) 