from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QProgressBar,
    QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import os
import json
import zipfile
import shutil
import requests
from datetime import datetime

class UpdateChecker(QThread):
    update_available = pyqtSignal(dict)
    no_update = pyqtSignal()
    error = pyqtSignal(str)
    progress = pyqtSignal(int)

    def run(self):
        try:
            # Читаем информацию об обновлении
            with open("updates/update_info.json", "r") as f:
                update_info = json.load(f)

            # Читаем текущую версию из настроек
            with open("app_settings.json", "r") as f:
                current_settings = json.load(f)
                current_version = current_settings["version"]["current"]

            # Сравниваем версии
            if update_info["version"] > current_version:
                self.update_available.emit(update_info)
            else:
                self.no_update.emit()

        except Exception as e:
            self.error.emit(str(e))

class UpdateInstaller(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, update_info):
        super().__init__()
        self.update_info = update_info

    def run(self):
        try:
            # Эмулируем процесс установки
            self.progress.emit(0)
            
            # Распаковываем архив с обновлением
            archive_path = f"updates/update_{self.update_info['version']}.zip"
            
            if not os.path.exists(archive_path):
                raise FileNotFoundError(f"Файл обновления не найден: {archive_path}")
            
            # Создаем временную директорию для распаковки
            temp_dir = "temp_update"
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            os.makedirs(temp_dir)
            
            self.progress.emit(30)
            
            # Распаковываем архив
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            self.progress.emit(60)
            
            # Копируем файлы из временной директории
            src_dir = os.path.join(temp_dir, f"app-{self.update_info['version']}")
            if not os.path.exists(src_dir):
                raise FileNotFoundError(f"Директория с обновлением не найдена: {src_dir}")
            
            # Копируем файлы
            for item in os.listdir(src_dir):
                s = os.path.join(src_dir, item)
                d = item
                if os.path.isfile(s):
                    shutil.copy2(s, d)
            
            self.progress.emit(90)
            
            # Обновляем версию в настройках
            with open("app_settings.json", "r") as f:
                settings = json.load(f)
            
            settings["version"]["current"] = self.update_info["version"]
            settings["version"]["last_check"] = datetime.now().isoformat()
            
            with open("app_settings.json", "w") as f:
                json.dump(settings, f, indent=4)
            
            # Очищаем временные файлы
            shutil.rmtree(temp_dir)
            
            self.progress.emit(100)
            self.finished.emit()

        except Exception as e:
            self.error.emit(str(e))

class UpdateDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Проверка обновлений")
        self.setFixedSize(400, 150)
        
        layout = QVBoxLayout()
        
        self.status_label = QLabel("Проверка наличия обновлений...")
        layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)
        
        self.update_button = QPushButton("Установить")
        self.update_button.setEnabled(False)
        self.update_button.clicked.connect(self.install_update)
        layout.addWidget(self.update_button)
        
        self.setLayout(layout)
        
        # Запускаем проверку обновлений
        self.checker = UpdateChecker()
        self.checker.update_available.connect(self.on_update_available)
        self.checker.no_update.connect(self.on_no_update)
        self.checker.error.connect(self.on_error)
        self.checker.progress.connect(self.progress_bar.setValue)
        self.checker.start()
        
        self.update_info = None
        self.installer = None

    def on_update_available(self, update_info):
        self.update_info = update_info
        self.status_label.setText(f"Доступно обновление {update_info['version']}\n{update_info['description']}")
        self.update_button.setEnabled(True)

    def on_no_update(self):
        self.status_label.setText("У вас установлена последняя версия")
        self.progress_bar.setValue(100)

    def on_error(self, error_msg):
        QMessageBox.critical(self, "Ошибка", f"Ошибка при проверке обновлений:\n{error_msg}")
        self.reject()

    def install_update(self):
        self.update_button.setEnabled(False)
        self.status_label.setText("Установка обновления...")
        
        self.installer = UpdateInstaller(self.update_info)
        self.installer.progress.connect(self.progress_bar.setValue)
        self.installer.finished.connect(self.on_install_finished)
        self.installer.error.connect(self.on_install_error)
        self.installer.start()

    def on_install_finished(self):
        QMessageBox.information(self, "Успех", "Обновление успешно установлено!\nПерезапустите приложение для применения изменений.")
        self.accept()

    def on_install_error(self, error_msg):
        QMessageBox.critical(self, "Ошибка", f"Ошибка при установке обновления:\n{error_msg}")
        self.update_button.setEnabled(True) 