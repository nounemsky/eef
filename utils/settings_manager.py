import json
import os
import logging
from datetime import datetime
from typing import Any, Dict


class SettingsManager:
    """Менеджер настроек приложения"""
    
    CURRENT_VERSION = "1.0.1"  # Увеличиваем версию из-за изменений в настройках
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.settings_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app_settings.json")
        self.default_settings = {
            "appearance": {
                "theme": "default",  # Исправляем на правильную тему по умолчанию
                "button_style": "macOS style",
            },
            "security": {
                "autolock_minutes": 15,
                "min_password_length": 8,
                "require_special_chars": True,
                "backup_count": 5
            },
            "interface": {
                "language": "ru",
                "show_password_strength": True,
                "show_favicons": True,
                "compact_mode": False
            },
            "version": {
                "current": self.CURRENT_VERSION,
                "last_check": None
            }
        }
        self.settings = self.load_settings()
        self._validate_and_migrate()

    def _validate_and_migrate(self):
        """Проверяет и мигрирует настройки при необходимости"""
        try:
            current_version = self.get_setting("version", "current", "1.0.0")
            if current_version != self.CURRENT_VERSION:
                self.logger.info(f"Обнаружена старая версия настроек: {current_version}")
                self._migrate_settings(current_version)
        except Exception as e:
            self.logger.error(f"Ошибка при миграции настроек: {e}")
            self.reset_settings()

    def _migrate_settings(self, old_version: str):
        """Мигрирует настройки со старой версии"""
        try:
            if old_version == "1.0.0":
                # Добавляем новые настройки безопасности
                if "security" not in self.settings:
                    self.settings["security"] = {}
                self.settings["security"].update({
                    "min_password_length": 8,
                    "require_special_chars": True,
                    "backup_count": 5
                })
                # Добавляем новые настройки интерфейса
                if "interface" not in self.settings:
                    self.settings["interface"] = {}
                self.settings["interface"].update({
                    "show_favicons": True,
                    "compact_mode": False
                })
                
            # Обновляем версию
            self.settings["version"]["current"] = self.CURRENT_VERSION
            self.settings["version"]["last_check"] = datetime.now().isoformat()
            
            # Сохраняем обновленные настройки
            self.save_settings()
            self.logger.info(f"Настройки успешно обновлены до версии {self.CURRENT_VERSION}")
            
        except Exception as e:
            self.logger.error(f"Ошибка при миграции настроек: {e}")
            raise

    def _validate_setting(self, category: str, key: str, value: Any) -> bool:
        """Проверяет корректность значения настройки"""
        try:
            if category == "security":
                if key == "autolock_minutes":
                    return isinstance(value, (int, float)) and 0 <= value <= 1440
                elif key == "min_password_length":
                    return isinstance(value, int) and 4 <= value <= 128
                elif key == "backup_count":
                    return isinstance(value, int) and 1 <= value <= 100
                elif key == "require_special_chars":
                    return isinstance(value, bool)
                    
            elif category == "interface":
                if key in ["show_password_strength", "show_favicons", "compact_mode"]:
                    return isinstance(value, bool)
                elif key == "language":
                    return value in ["ru", "en"]
                    
            elif category == "appearance":
                if key == "theme":
                    return value in ["default", "dark", "light", "cyberpunk"]
                elif key == "button_style":
                    return isinstance(value, str)
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка валидации настройки {category}.{key}: {e}")
            return False

    def load_settings(self) -> Dict[str, Any]:
        """Загружает настройки из файла"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    # Проверяем и добавляем недостающие настройки
                    for category, values in self.default_settings.items():
                        if category not in settings:
                            settings[category] = values
                        else:
                            for key, value in values.items():
                                if key not in settings[category]:
                                    settings[category][key] = value
                                # Проверяем корректность значения
                                elif not self._validate_setting(category, key, settings[category][key]):
                                    self.logger.warning(f"Некорректное значение {category}.{key}, используем значение по умолчанию")
                                    settings[category][key] = value
                    return settings
            return self.default_settings.copy()
        except Exception as e:
            self.logger.error(f"Ошибка загрузки настроек: {e}")
            return self.default_settings.copy()

    def save_settings(self) -> bool:
        """Сохраняет настройки в файл"""
        try:
            # Создаем директорию для файла настроек, если её нет
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            
            # Сохраняем во временный файл
            temp_file = f"{self.settings_file}.tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
                
            # Заменяем основной файл
            os.replace(temp_file, self.settings_file)
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка сохранения настроек: {e}")
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
            return False

    def get_setting(self, category: str, key: str, default: Any = None) -> Any:
        """Получает значение настройки"""
        try:
            value = self.settings[category][key]
            if self._validate_setting(category, key, value):
                return value
            self.logger.warning(f"Некорректное значение {category}.{key}, возвращаем значение по умолчанию")
            return default if default is not None else self.default_settings[category][key]
        except KeyError:
            return default if default is not None else self.default_settings[category][key]

    def set_setting(self, category: str, key: str, value: Any) -> bool:
        """Устанавливает значение настройки"""
        try:
            if not self._validate_setting(category, key, value):
                self.logger.error(f"Попытка установить некорректное значение для {category}.{key}")
                return False
                
            if category not in self.settings:
                self.settings[category] = {}
            self.settings[category][key] = value
            return self.save_settings()
            
        except Exception as e:
            self.logger.error(f"Ошибка установки настройки {category}.{key}: {e}")
            return False

    def reset_settings(self) -> bool:
        """Сбрасывает настройки на значения по умолчанию"""
        try:
            self.settings = self.default_settings.copy()
            return self.save_settings()
        except Exception as e:
            self.logger.error(f"Ошибка сброса настроек: {e}")
            return False

    def get_version(self):
        """Получает текущую версию приложения"""
        return self.get_setting("version", "current")

    def set_version(self, version):
        """Устанавливает новую версию приложения"""
        self.set_setting("version", "current", version)
        self.set_setting("version", "last_check", datetime.now().isoformat()) 