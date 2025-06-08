from PyQt6.QtCore import QtMsgType, qInstallMessageHandler
import sys

def qt_message_handler(mode, context, message):
    """Обработчик сообщений Qt для логирования"""
    # Определяем тип сообщения
    mode_str = {
        QtMsgType.QtDebugMsg: "Debug",
        QtMsgType.QtWarningMsg: "Warning",
        QtMsgType.QtCriticalMsg: "Critical",
        QtMsgType.QtFatalMsg: "Fatal",
        QtMsgType.QtInfoMsg: "Info"
    }.get(mode, "Unknown")
    
    # Игнорируем некоторые предупреждения
    ignored_messages = [
        "Unknown property",
        "QLayout: Attempting to add QLayout"
    ]
    
    # Пропускаем игнорируемые сообщения
    if any(msg in message for msg in ignored_messages):
        return
        
    # Выводим сообщение с типом и контекстом
    print(f'[Qt {mode_str}] {message} ({context.file}:{context.line})')
    
    # Для критических и фатальных ошибок добавляем дополнительную информацию
    if mode in [QtMsgType.QtCriticalMsg, QtMsgType.QtFatalMsg]:
        print(f"Context: {context}") 