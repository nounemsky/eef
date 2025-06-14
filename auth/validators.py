import re
from urllib.parse import urlparse


class DataValidator:
    @staticmethod
    def sanitize_string(value: str) -> str:
        """Очищает строку от потенциально опасных символов"""
        return value.strip()

    @staticmethod
    def validate_service(service: str) -> bool:
        """Проверяет название сервиса"""
        if not isinstance(service, str):
            return False
        service = service.strip()
        if not service or len(service) > 100:
            return False
        return True

    @staticmethod
    def validate_password(password: str) -> bool:
        """Проверяет пароль"""
        if not isinstance(password, str):
            return False
        password = password.strip()
        if not password or len(password) > 1000:
            return False
        return True

    @staticmethod
    def validate_url(url: str) -> bool:
        """Проверяет URL"""
        if not url:
            return True  # URL может быть пустым
        if not isinstance(url, str):
            return False
        url = url.strip()
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

    @staticmethod
    def validate_email(email: str) -> bool:
        """Проверяет email"""
        if not email:
            return True  # Email может быть пустым
        if not isinstance(email, str):
            return False
        email = email.strip()
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Проверяет телефон"""
        if not phone:
            return True  # Телефон может быть пустым
        if not isinstance(phone, str):
            return False
        phone = phone.strip()
        # Удаляем все кроме цифр и проверяем длину
        digits = re.sub(r'\D', '', phone)
        return 10 <= len(digits) <= 15

    @staticmethod
    def validate_notes(notes: str) -> bool:
        """Проверяет заметки"""
        if not notes:
            return True
        if not isinstance(notes, str):
            return False
        notes = notes.strip()
        return len(notes) <= 1000

    @staticmethod
    def validate_category(category: str) -> bool:
        """Проверяет категорию"""
        if not isinstance(category, str):
            return False
        category = category.strip()
        if not category:
            return False
        return len(category) <= 50 