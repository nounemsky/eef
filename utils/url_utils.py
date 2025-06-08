from urllib.parse import urlparse

def extract_domain(url: str) -> str:
    """
    Извлекает домен из URL.
    
    Args:
        url (str): URL для обработки
        
    Returns:
        str: Домен без протокола и www
        
    Examples:
        >>> extract_domain('https://www.example.com/path')
        'example.com'
        >>> extract_domain('http://subdomain.example.com')
        'subdomain.example.com'
        >>> extract_domain('invalid-url')
        'invalid-url'
    """
    try:
        # Добавляем протокол, если его нет
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
            
        parsed = urlparse(url)
        domain = parsed.netloc
        
        # Убираем www. если есть
        if domain.startswith('www.'):
            domain = domain[4:]
            
        return domain if domain else url
    except Exception:
        # В случае некорректного URL возвращаем исходную строку
        return url 