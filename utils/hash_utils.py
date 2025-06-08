import hashlib

def md5_hash(text: str) -> str:
    """
    Создает MD5 хеш из строки.
    
    Args:
        text (str): Текст для хеширования
        
    Returns:
        str: MD5 хеш в виде шестнадцатеричной строки
    """
    return hashlib.md5(text.encode('utf-8')).hexdigest() 