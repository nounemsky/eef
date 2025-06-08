import json
import os
from typing import Any, Dict


class Config:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config: Dict[str, Any] = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации из файла"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self.get_default_config()

    def save_config(self) -> None:
        """Сохранение конфигурации в файл"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)

    def get_default_config(self) -> Dict[str, Any]:
        """Возвращает конфигурацию по умолчанию"""
        return {
            "window": {
                "width": 1200,
                "height": 800,
                "remember_position": True,
                "position_x": None,
                "position_y": None
            },
            "security": {
                "auto_lock_timeout": 300,  # 5 минут
                "password_length": 16,
                "use_special_chars": True,
                "backup_enabled": True,
                "backup_interval": 86400  # 24 часа
            },
            "appearance": {
                "theme": "dark",
                "font_size": 12,
                "show_toolbar": True,
                "show_statusbar": True
            },
            "updates": {
                "check_on_startup": True,
                "auto_update": False
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Получение значения по ключу"""
        try:
            keys = key.split('.')
            value = self.config
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any) -> None:
        """Установка значения по ключу"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save_config() 