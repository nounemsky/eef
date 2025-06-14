from PyQt6.QtCore import QtMsgType, qInstallMessageHandler
import sys
import logging
import traceback
from typing import Dict, Set


class QtMessageHandler:
    """Обработчик сообщений Qt с фильтрацией и логированием"""
    
    def __init__(self):
        self.logger = logging.getLogger("Qt")
        self.message_counts: Dict[str, int] = {}
        self.max_repeated_messages = 10
        self.ignored_patterns: Set[str] = {
            "QLayout: Attempting to add QLayout",
            "QSocketNotifier: Invalid socket",
            "QPixmap::scaled: Pixmap is a null pixmap",
            "libpng warning: iCCP: known incorrect sRGB profile"
        }
        
    def should_ignore(self, message: str) -> bool:
        """Проверяет, нужно ли игнорировать сообщение"""
        return any(pattern in message for pattern in self.ignored_patterns)
        
    def handle_message(self, mode: QtMsgType, context, message: str):
        """Обрабатывает сообщение Qt"""
        if self.should_ignore(message):
            return
            
        # Определяем тип сообщения и уровень логирования
        mode_info = {
            QtMsgType.QtDebugMsg: ("Debug", logging.DEBUG),
            QtMsgType.QtWarningMsg: ("Warning", logging.WARNING),
            QtMsgType.QtCriticalMsg: ("Critical", logging.ERROR),
            QtMsgType.QtFatalMsg: ("Fatal", logging.CRITICAL),
            QtMsgType.QtInfoMsg: ("Info", logging.INFO)
        }.get(mode, ("Unknown", logging.WARNING))
        
        mode_str, log_level = mode_info
        
        # Формируем сообщение
        log_message = f"[Qt {mode_str}] {message}"
        if context.file:
            log_message += f" ({context.file}:{context.line})"
            
        # Проверяем на повторяющиеся сообщения
        if message in self.message_counts:
            self.message_counts[message] += 1
            if self.message_counts[message] > self.max_repeated_messages:
                return
            if self.message_counts[message] == self.max_repeated_messages:
                log_message += " (дальнейшие сообщения будут пропущены)"
        else:
            self.message_counts[message] = 1
            
        # Логируем сообщение
        self.logger.log(log_level, log_message)
        
        # Для критических и фатальных ошибок добавляем стек вызовов
        if mode in [QtMsgType.QtCriticalMsg, QtMsgType.QtFatalMsg]:
            self.logger.error(f"Контекст: {context}")
            self.logger.error("Стек вызовов:\n" + "".join(traceback.format_stack()))
            
        # Для фатальных ошибок завершаем приложение
        if mode == QtMsgType.QtFatalMsg:
            self.logger.critical("Получена фатальная ошибка Qt, завершение приложения")
            sys.exit(1)


# Создаем глобальный обработчик
qt_handler = QtMessageHandler()


def qt_message_handler(mode, context, message):
    """Функция-обработчик для установки через qInstallMessageHandler"""
    qt_handler.handle_message(mode, context, message) 