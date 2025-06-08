import os
import time
import shutil
from .crypto_manager import CryptoManagerV2


class BackupManager:
    BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backups")
    MAX_BACKUPS = 5  # Максимальное количество резервных копий

    def __init__(self, crypto_manager: CryptoManagerV2):
        self.crypto = crypto_manager
        self._ensure_backup_dir_exists()

    @classmethod
    def _ensure_backup_dir_exists(cls):
        if not os.path.exists(cls.BACKUP_DIR):
            os.makedirs(cls.BACKUP_DIR, mode=0o700)

    def _get_backup_path(self, original_path: str, timestamp: int = None) -> str:
        base_name = os.path.basename(original_path)
        name, ext = os.path.splitext(base_name)
        timestamp = timestamp or int(time.time())
        return os.path.join(self.BACKUP_DIR, f"{name}_backup_{timestamp}{ext}")

    def create_backup(self, file_path: str, data: dict) -> bool:
        """Создает зашифрованную резервную копию"""
        try:
            # Шифруем данные с дополнительной солью для бэкапа
            backup_data = {
                "data": data,
                "original_path": file_path,
                "timestamp": int(time.time())
            }
            encrypted = self.crypto.encrypt_data(backup_data)
            
            # Сохраняем бэкап
            backup_path = self._get_backup_path(file_path)
            with open(backup_path, "w") as f:
                f.write(encrypted)

            # Проверяем и удаляем старые бэкапы
            self._cleanup_old_backups(file_path)
            return True
        except Exception as e:
            print(f"Ошибка создания бэкапа: {str(e)}")
            return False

    def restore_from_backup(self, original_path: str, timestamp: int = None) -> dict | None:
        """Восстанавливает данные из бэкапа"""
        try:
            # Находим нужный бэкап
            backup_path = self._get_backup_path(original_path, timestamp)
            if not os.path.exists(backup_path):
                return None

            # Расшифровываем и проверяем данные
            with open(backup_path, "r") as f:
                decrypted = self.crypto.decrypt_data(f.read())
                if decrypted.get("original_path") != original_path:
                    raise ValueError("Несоответствие пути файла!")
                return decrypted.get("data")
        except Exception as e:
            print(f"Ошибка восстановления из бэкапа: {str(e)}")
            return None

    def _cleanup_old_backups(self, original_path: str):
        """Удаляет старые резервные копии, оставляя только MAX_BACKUPS последних"""
        try:
            base_name = os.path.basename(original_path)
            name, ext = os.path.splitext(base_name)
            pattern = f"{name}_backup_*{ext}"
            
            # Получаем список всех бэкапов для данного файла
            backups = []
            for filename in os.listdir(self.BACKUP_DIR):
                if filename.startswith(f"{name}_backup_") and filename.endswith(ext):
                    full_path = os.path.join(self.BACKUP_DIR, filename)
                    backups.append((os.path.getmtime(full_path), full_path))
            
            # Сортируем по времени создания (новые в конце)
            backups.sort()
            
            # Удаляем старые бэкапы
            while len(backups) > self.MAX_BACKUPS:
                _, path = backups.pop(0)
                try:
                    os.remove(path)
                except:
                    pass
        except Exception as e:
            print(f"Ошибка при очистке старых бэкапов: {str(e)}") 