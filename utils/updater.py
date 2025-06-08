import os
import json
import requests
from PyQt6.QtCore import QThread, pyqtSignal
import sys
import subprocess
import shutil
from datetime import datetime

# Конфигурация GitHub
GITHUB_CONFIG = {
    "username": "YOUR_USERNAME",  # Ваше имя пользователя на GitHub
    "repo": "YOUR_REPO",         # Название репозитория
    "branch": "main"             # Основная ветка
}

class UpdateChecker(QThread):
    update_available = pyqtSignal(str, str)  # version, changelog
    no_update = pyqtSignal()
    error = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.settings_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app_settings.json")
        self.updates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "updates")
        os.makedirs(self.updates_dir, exist_ok=True)
        self.current_version = self._get_current_version()
        print(f"[DEBUG] Текущая версия: {self.current_version}")
    
    def _get_current_version(self):
        """Получает текущую версию из настроек"""
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                version = settings.get('version', {}).get('current', '1.0.0')
                print(f"[DEBUG] Прочитана версия из настроек: {version}")
                return version
        except Exception as e:
            print(f"[DEBUG] Ошибка при чтении версии: {e}")
            return '1.0.0'
    
    def _get_latest_update(self):
        """Проверяет наличие обновления в локальной директории"""
        try:
            updates_info_file = os.path.join(self.updates_dir, "update_info.json")
            print(f"[DEBUG] Путь к файлу обновлений: {updates_info_file}")
            if not os.path.exists(updates_info_file):
                print("[DEBUG] Файл update_info.json не найден")
                return None
                
            with open(updates_info_file, 'r', encoding='utf-8') as f:
                update_info = json.load(f)
                print(f"[DEBUG] Информация об обновлении: {update_info}")
                return update_info
        except Exception as e:
            print(f"[DEBUG] Ошибка при чтении информации об обновлении: {e}")
            return None
    
    def run(self):
        try:
            update_info = self._get_latest_update()
            if not update_info:
                print("[DEBUG] Нет информации об обновлении")
                self.no_update.emit()
                return
                
            latest_version = update_info.get('version')
            print(f"[DEBUG] Последняя доступная версия: {latest_version}")
            
            if not latest_version:
                print("[DEBUG] Версия не указана в update_info.json")
                self.error.emit("Некорректная информация об обновлении")
                return
                
            comparison = self._compare_versions(latest_version, self.current_version)
            print(f"[DEBUG] Результат сравнения версий: {comparison}")
            
            if comparison > 0:
                print("[DEBUG] Доступно обновление")
                self.update_available.emit(
                    latest_version,
                    update_info.get('changelog', 'Нет информации об изменениях')
                )
            else:
                print("[DEBUG] Обновление не требуется")
                self.no_update.emit()
                
        except Exception as e:
            print(f"[DEBUG] Ошибка при проверке обновлений: {e}")
            self.error.emit(str(e))
    
    def _compare_versions(self, version1, version2):
        """Сравнивает версии в формате x.y.z"""
        try:
            v1_parts = [int(x) for x in version1.split('.')]
            v2_parts = [int(x) for x in version2.split('.')]
            
            for i in range(max(len(v1_parts), len(v2_parts))):
                v1 = v1_parts[i] if i < len(v1_parts) else 0
                v2 = v2_parts[i] if i < len(v2_parts) else 0
                if v1 > v2:
                    return 1
                elif v1 < v2:
                    return -1
            return 0
        except Exception as e:
            print(f"[DEBUG] Ошибка при сравнении версий: {e}")
            return 0

class UpdateInstaller(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, version):
        super().__init__()
        self.version = version
        base_dir = os.path.dirname(os.path.dirname(__file__))
        self.updates_dir = os.path.join(base_dir, "updates")
        self.temp_dir = os.path.join(base_dir, 'temp_update')
        self.settings_file = os.path.join(base_dir, "app_settings.json")
    
    def _update_version(self):
        """Обновляет версию в настройках"""
        try:
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)
            
            settings['version']['current'] = self.version
            settings['version']['last_check'] = datetime.now().isoformat()
            
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=4)
        except Exception as e:
            print(f"Ошибка при обновлении версии: {e}")
    
    def run(self):
        try:
            # Проверяем наличие файла обновления
            update_file = os.path.join(self.updates_dir, f"update_{self.version}.zip")
            if not os.path.exists(update_file):
                self.finished.emit(False, "Файл обновления не найден")
                return
            
            # Создаем временную директорию
            if not os.path.exists(self.temp_dir):
                os.makedirs(self.temp_dir)
            
            # Создаем бэкап
            self.progress.emit("Создание резервной копии...")
            backup_dir = os.path.join(os.path.dirname(self.temp_dir), 
                                    'backups', 
                                    f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            shutil.copytree(os.path.dirname(self.temp_dir), backup_dir, 
                           ignore=shutil.ignore_patterns('backups*', 'temp_update*', '.git*', '__pycache__*', '.venv*', 'updates*'))
            
            # Распаковываем обновление
            self.progress.emit("Установка обновления...")
            shutil.unpack_archive(update_file, self.temp_dir)
            
            # Обновляем файлы
            source_dir = os.path.join(self.temp_dir, f"app-{self.version}")
            target_dir = os.path.dirname(self.temp_dir)
            
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    src_path = os.path.join(root, file)
                    rel_path = os.path.relpath(src_path, source_dir)
                    dst_path = os.path.join(target_dir, rel_path)
                    
                    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                    shutil.copy2(src_path, dst_path)
            
            # Обновляем версию в настройках
            self._update_version()
            
            # Очищаем временные файлы
            self.progress.emit("Завершение установки...")
            shutil.rmtree(self.temp_dir)
            
            self.finished.emit(True, "Обновление успешно установлено")
            
            # Перезапускаем приложение
            python = sys.executable
            subprocess.Popen([python, os.path.join(target_dir, 'main.py')])
            sys.exit(0)
            
        except Exception as e:
            self.finished.emit(False, f"Ошибка при установке обновления: {str(e)}") 