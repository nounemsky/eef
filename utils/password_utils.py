import re

def password_strength(password: str) -> int:
    """
    Оценивает сложность пароля по шкале от 0 до 5.
    
    Критерии:
    1. Длина >= 8 символов
    2. Наличие цифр
    3. Наличие букв в нижнем регистре
    4. Наличие букв в верхнем регистре
    5. Наличие специальных символов
    
    Args:
        password (str): Пароль для проверки
        
    Returns:
        int: Оценка сложности от 0 до 5
    """
    score = 0
    
    if not password:
        return score
        
    # Длина
    if len(password) >= 8:
        score += 1
        
    # Цифры
    if re.search(r"\d", password):
        score += 1
        
    # Буквы в нижнем регистре
    if re.search(r"[a-z]", password):
        score += 1
        
    # Буквы в верхнем регистре
    if re.search(r"[A-Z]", password):
        score += 1
        
    # Специальные символы
    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        score += 1
        
    return score 