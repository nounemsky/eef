import os
import time
import shutil
from typing import Optional
from datetime import datetime, timedelta

class CacheManager:
    # Значения по умолчанию для настроек кэша
    DEFAULT_SETTINGS = {
        "max_favicon_size_mb": 10,
        "max_temp_size_mb": 50,
        "cleanup_interval_days": 7,
        "max_favicons": 1000
    }

    def __init__(self, settings_manager):
        self.settings_manager = settings_manager
        self.base_cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app_cache")
        self.favicons_dir = os.path.join(self.base_cache_dir, "favicons")
        self.temp_dir = os.path.join(self.base_cache_dir, "temp")
        self.updates_dir = os.path.join(self.base_cache_dir, "updates")
        
        # Создаем директории если они не существуют
        for directory in [self.base_cache_dir, self.favicons_dir, self.temp_dir, self.updates_dir]:
            os.makedirs(directory, exist_ok=True)

    def get_setting(self, key: str) -> any:
        """Получает настройку кэша с поддержкой значений по умолчанию"""
        try:
            return self.settings_manager.get_setting("cache", key)
        except (AttributeError, KeyError, FileNotFoundError):
            return self.DEFAULT_SETTINGS.get(key)

    def get_directory_size(self, directory: str) -> float:
        """Возвращает размер директории в мегабайтах"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size / (1024 * 1024)  # Конвертируем в МБ

    def cleanup_old_files(self, directory: str, days: int) -> None:
        """Удаляет файлы старше указанного количества дней"""
        current_time = time.time()
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                file_time = os.path.getmtime(filepath)
                if current_time - file_time > days * 86400:  # 86400 секунд в дне
                    try:
                        os.remove(filepath)
                    except (PermissionError, FileNotFoundError) as e:
                        print(f"Ошибка при удалении {filepath}: {e}")

    def cleanup_by_size(self, directory: str, max_size_mb: float) -> None:
        """Удаляет старые файлы, пока размер директории не станет меньше max_size_mb"""
        while self.get_directory_size(directory) > max_size_mb:
            oldest_file = None
            oldest_time = float('inf')
            
            for filename in os.listdir(directory):
                filepath = os.path.join(directory, filename)
                if os.path.isfile(filepath):
                    try:
                        file_time = os.path.getmtime(filepath)
                        if file_time < oldest_time:
                            oldest_time = file_time
                            oldest_file = filepath
                    except (OSError, FileNotFoundError):
                        continue
            
            if oldest_file:
                try:
                    os.remove(oldest_file)
                except (PermissionError, FileNotFoundError):
                    break
            else:
                break

    def cleanup_favicons(self) -> None:
        """Очищает кэш фавиконок"""
        max_size = self.get_setting("max_favicon_size_mb")
        max_count = self.get_setting("max_favicons")
        
        # Удаляем по размеру
        self.cleanup_by_size(self.favicons_dir, max_size)
        
        # Удаляем по количеству
        try:
            files = sorted(os.listdir(self.favicons_dir), 
                          key=lambda x: os.path.getmtime(os.path.join(self.favicons_dir, x)))
            if len(files) > max_count:
                for f in files[:-max_count]:  # Оставляем только max_count самых новых файлов
                    try:
                        os.remove(os.path.join(self.favicons_dir, f))
                    except (PermissionError, FileNotFoundError):
                        continue
        except (OSError, FileNotFoundError) as e:
            print(f"Ошибка при очистке фавиконок: {e}")

    def cleanup_temp(self) -> None:
        """Очищает временные файлы"""
        max_size = self.get_setting("max_temp_size_mb")
        days = self.get_setting("cleanup_interval_days")
        
        self.cleanup_old_files(self.temp_dir, days)
        self.cleanup_by_size(self.temp_dir, max_size)

    def cleanup_all(self) -> None:
        """Очищает все кэши"""
        try:
            self.cleanup_favicons()
            self.cleanup_temp()
        except Exception as e:
            print(f"Ошибка при очистке кэша: {e}")

    def clear_all_cache(self) -> None:
        """Полностью очищает все кэши"""
        for directory in [self.favicons_dir, self.temp_dir, self.updates_dir]:
            try:
                for filename in os.listdir(directory):
                    filepath = os.path.join(directory, filename)
                    try:
                        if os.path.isfile(filepath):
                            os.remove(filepath)
                    except Exception as e:
                        print(f"Ошибка при удалении {filepath}: {e}")
            except (OSError, FileNotFoundError) as e:
                print(f"Ошибка при очистке директории {directory}: {e}")

    def get_cache_stats(self) -> dict:
        """Возвращает статистику использования кэша"""
        try:
            return {
                "favicons_size_mb": self.get_directory_size(self.favicons_dir),
                "temp_size_mb": self.get_directory_size(self.temp_dir),
                "updates_size_mb": self.get_directory_size(self.updates_dir),
                "favicons_count": len(os.listdir(self.favicons_dir)),
                "temp_count": len(os.listdir(self.temp_dir)),
                "updates_count": len(os.listdir(self.updates_dir))
            }
        except Exception as e:
            print(f"Ошибка при получении статистики кэша: {e}")
            return {
                "favicons_size_mb": 0,
                "temp_size_mb": 0,
                "updates_size_mb": 0,
                "favicons_count": 0,
                "temp_count": 0,
                "updates_count": 0
            } 