import sys
import os
import platform
import logging
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import qInstallMessageHandler, QDir
from PyQt6.QtGui import QFontDatabase
from ui.ui import PasswordManagerUI
from auth.password_manager import PasswordManager
from styles import APP_STYLES
from utils.qt_handler import qt_message_handler
from utils.settings_manager import SettingsManager


def setup_logging():
    """Настраивает систему логирования"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, 'app.log')),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def check_environment():
    """Проверяет окружение приложения"""
    # Проверяем версию Python
    if sys.version_info < (3, 9):
        raise RuntimeError("Требуется Python 3.9 или выше")
    
    # Проверяем наличие необходимых директорий
    required_dirs = ['vaults', 'app_cache', 'backups']
    for dir_name in required_dirs:
        os.makedirs(dir_name, exist_ok=True)
    
    # Проверяем права на запись
    for dir_name in required_dirs:
        test_file = os.path.join(dir_name, '.test')
        try:
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
        except Exception as e:
            raise RuntimeError(f"Нет прав на запись в директорию {dir_name}: {e}")

def load_fonts(folder="fonts"):
    """Загружает шрифты из указанной папки в приложение"""
    logger = logging.getLogger(__name__)
    loaded_fonts = []
    
    try:
        if not os.path.exists(folder):
            logger.warning(f"Папка со шрифтами не найдена: {folder}")
            return loaded_fonts

        for filename in os.listdir(folder):
            if filename.lower().endswith((".ttf", ".otf")):
                font_path = os.path.join(folder, filename)
                try:
                    font_id = QFontDatabase.addApplicationFont(font_path)
                    if font_id != -1:
                        font_families = QFontDatabase.applicationFontFamilies(font_id)
                        loaded_fonts.extend(font_families)
                        logger.info(f"Загружен шрифт: {', '.join(font_families)}")
                    else:
                        logger.error(f"Ошибка загрузки шрифта: {filename}")
                except Exception as e:
                    logger.error(f"Ошибка при загрузке шрифта {filename}: {e}")

        if not loaded_fonts:
            logger.warning("Не удалось загрузить ни одного шрифта")
        else:
            logger.info(f"Всего загружено шрифтов: {len(loaded_fonts)}")

    except Exception as e:
        logger.error(f"Ошибка при загрузке шрифтов: {e}")

    return loaded_fonts

def show_error_and_exit(message):
    """Показывает сообщение об ошибке и завершает приложение"""
    if QApplication.instance() is None:
        QApplication([])
    QMessageBox.critical(None, "Критическая ошибка", message)
    sys.exit(1)

def main():
    try:
        # Инициализируем логирование
        logger = setup_logging()
        logger.info("Запуск приложения...")
        
        # Проверяем окружение
        try:
            check_environment()
        except Exception as e:
            show_error_and_exit(str(e))
        
        # Устанавливаем обработчик сообщений Qt
        qInstallMessageHandler(qt_message_handler)
        
        # Создаем приложение
        app = QApplication(sys.argv)
        
        # Устанавливаем рабочую директорию
        app_dir = os.path.dirname(os.path.abspath(__file__))
        QDir.setCurrent(app_dir)
        
        # Загружаем шрифты
        loaded_fonts = load_fonts()
        if loaded_fonts:
            logger.info(f"Загружены шрифты: {', '.join(loaded_fonts)}")
        
        # Инициализируем менеджер настроек
        settings_manager = SettingsManager()
        
        # Создаем главное окно
        window = PasswordManagerUI(APP_STYLES)
        window.show()
        
        logger.info("Приложение успешно запущено")
        return app.exec()
        
    except Exception as e:
        logger.critical(f"Критическая ошибка при запуске: {e}", exc_info=True)
        show_error_and_exit(f"Критическая ошибка при запуске приложения:\n{str(e)}")

if __name__ == "__main__":
    sys.exit(main())
