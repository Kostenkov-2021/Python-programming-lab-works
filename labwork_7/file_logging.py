import logging.config


def setup_file_logging(filename: str = "currency.log") -> logging.Logger:
    """
    Настраивает логирование в файл.
    
    Args:
        filename: Имя файла для логирования
    
    Returns:
        Настроенный логгер
    """
    file_logger = logging.getLogger("currency_file")
    file_logger.setLevel(logging.INFO)
    
    # Очищаем существующие обработчики
    file_logger.handlers.clear()
    
    # Создаем обработчик для файла
    file_handler = logging.FileHandler(filename, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # Форматтер для файла
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    
    file_logger.addHandler(file_handler)
    file_logger.propagate = False
    
    return file_logger


# Пример использования файлового логирования
file_logger = setup_file_logging("currencies.log")

@logger(handle=file_logger)
def get_currencies_file_logged(
    currency_codes: List[str],
    url: str = "https://www.cbr-xml-daily.ru/daily_json.js"
) -> Dict[str, float]:
    """Обернутая версия get_currencies с файловым логированием."""
    return get_currencies(currency_codes, url)