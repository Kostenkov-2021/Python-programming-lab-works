import json
import requests
from typing import Dict, List, Optional
from urllib.parse import urljoin
from logger_decorator import logger


def get_currencies(
    currency_codes: List[str],
    url: str = "https://www.cbr-xml-daily.ru/daily_json.js",
    timeout: float = 10.0
) -> Dict[str, float]:
    """
    Получает курсы валют от API ЦБ РФ.
    
    Args:
        currency_codes: Список кодов валют (например, ['USD', 'EUR'])
        url: URL API ЦБ РФ
        timeout: Таймаут запроса в секундах
    
    Returns:
        Словарь вида {'USD': 93.25, 'EUR': 101.7}
    
    Raises:
        ConnectionError: Если API недоступен
        ValueError: Если получен некорректный JSON
        KeyError: Если отсутствует ключ 'Valute' или валюта
        TypeError: Если курс валюты имеет неверный тип
        
    Note:
        Функция не содержит логирования - только бизнес-логику.
        Все исключения пробрасываются для обработки декоратором.
    """
    
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as e:
        raise ConnectionError(f"Ошибка подключения к API: {str(e)}") from e
    
    try:
        data = response.json()
    except json.JSONDecodeError as e:
        raise ValueError(f"Некорректный JSON в ответе: {str(e)}") from e
    
    if 'Valute' not in data:
        raise KeyError("Ключ 'Valute' отсутствует в ответе API")
    
    result = {}
    valutes = data['Valute']
    
    for code in currency_codes:
        if code not in valutes:
            raise KeyError(f"Валюта '{code}' отсутствует в данных API")
        
        currency_data = valutes[code]
        if 'Value' not in currency_data:
            raise KeyError(f"Ключ 'Value' отсутствует для валюты '{code}'")
        
        try:
            rate = float(currency_data['Value'])
        except (TypeError, ValueError) as e:
            raise TypeError(
                f"Невозможно преобразовать курс валюты '{code}' в число: "
                f"{currency_data['Value']}"
            ) from e
        
        result[code] = rate
    
    return result


# Пример использования с декоратором
@logger(handle=sys.stdout)
def get_currencies_logged(
    currency_codes: List[str],
    url: str = "https://www.cbr-xml-daily.ru/daily_json.js"
) -> Dict[str, float]:
    """Обернутая версия get_currencies с логированием."""
    return get_currencies(currency_codes, url)