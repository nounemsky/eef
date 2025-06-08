import json
import os
from datetime import datetime

class SettingsManager:
    """Менеджер настроек приложения"""
    
    def __init__(self):
        self.settings_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app_settings.json")
        self.default_settings = {
            "appearance": {
                "theme": "Dark Theme",
                "button_style": "macOS style",
            },
            "security": {
                "autolock_minutes": 15,
            },
            "interface": {
                "language": "ru",
                "show_password_strength": True,
            },
            "version": {
                "current": "1.0.0",
                "last_check": None
            }
        }
        self.settings = self.load_settings()
        
        # Проверяем наличие информации о версии
        if "version" not in self.settings:
            self.settings["version"] = self.default_settings["version"]
            self.save_settings()

    def load_settings(self):
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
                    return settings
            return self.default_settings.copy()
        except Exception as e:
            print(f"Ошибка загрузки настроек: {str(e)}")
            return self.default_settings.copy()

    def save_settings(self):
        """Сохраняет настройки в файл"""
        try:
            # Создаем директорию для файла настроек, если её нет
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Ошибка сохранения настроек: {str(e)}")
            return False

    def get_setting(self, category: str, key: str, default=None):
        """Получает значение настройки"""
        try:
            return self.settings[category][key]
        except KeyError:
            if default is not None:
                return default
            return self.default_settings[category][key]

    def set_setting(self, category: str, key: str, value):
        """Устанавливает значение настройки"""
        if category not in self.settings:
            self.settings[category] = {}
        self.settings[category][key] = value
        return self.save_settings()

    def reset_settings(self):
        """Сбрасывает настройки на значения по умолчанию"""
        self.settings = self.default_settings.copy()
        return self.save_settings()

    def get_version(self):
        """Получает текущую версию приложения"""
        return self.get_setting("version", "current")

    def set_version(self, version):
        """Устанавливает новую версию приложения"""
        self.set_setting("version", "current", version)
        self.set_setting("version", "last_check", datetime.now().isoformat()) 