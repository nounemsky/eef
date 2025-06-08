import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import qInstallMessageHandler
from ui.ui import PasswordManagerUI
from auth.password_manager import PasswordManager
from styles import APP_STYLES
from utils.qt_handler import qt_message_handler

def main():
    # Устанавливаем обработчик сообщений Qt
    qInstallMessageHandler(qt_message_handler)
    
    app = QApplication(sys.argv)
    
    # Создаем UI без менеджера паролей
    window = PasswordManagerUI(APP_STYLES)
    window.show()
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
