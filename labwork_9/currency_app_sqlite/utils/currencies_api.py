"""
Модуль для работы с API курсов валют ЦБ РФ.

Содержит функцию get_currencies для получения актуальных курсов валют.
"""

import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP


def get_currencies(
    currency_codes: Optional[List[str]] = None,
    url: str = "https://www.cbr-xml-daily.ru/daily_json.js",
    timeout: float = 10.0
) -> Dict[str, float]:
    """
    Получить курсы валют от API ЦБ РФ.
    
    Args:
        currency_codes: Список кодов валют для получения (если None - все доступные)
        url: URL API ЦБ РФ
        timeout: Таймаут запроса в секундах
    
    Returns:
        Словарь вида {'USD': 93.25, 'EUR': 101.7}
    
    Raises:
        ConnectionError: Если API недоступен
        ValueError: Если получен некорректный JSON
        KeyError: Если отсутствует ключ 'Valute' или валюта
        TypeError: Если курс валюты имеет неверный тип
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
    
    # Если не указаны конкретные валюты, возвращаем все
    if currency_codes is None:
        currency_codes = list(valutes.keys())
    
    for code in currency_codes:
        if code not in valutes:
            raise KeyError(f"Валюта '{code}' отсутствует в данных API")
        
        currency_data = valutes[code]
        
        # Проверяем наличие всех необходимых полей
        required_fields = ['Value', 'Nominal', 'CharCode', 'Name']
        for field in required_fields:
            if field not in currency_data:
                raise KeyError(f"Ключ '{field}' отсутствует для валюты '{code}'")
        
        # Получаем и валидируем значение курса
        value_str = str(currency_data['Value'])
        nominal = currency_data['Nominal']
        
        try:
            # Преобразуем строку с запятой в число
            value_str = value_str.replace(',', '.')
            value = float(value_str)
            
            # Корректируем курс с учетом номинала
            actual_value = value / nominal
            
            # Округляем до 4 знаков после запятой
            actual_value = Decimal(str(actual_value)).quantize(
                Decimal('0.0001'), rounding=ROUND_HALF_UP
            )
            
            result[code] = float(actual_value)
            
        except (ValueError, TypeError) as e:
            raise TypeError(
                f"Невозможно преобразовать курс валюты '{code}' в число: "
                f"{currency_data['Value']}. Ошибка: {str(e)}"
            ) from e
    
    return result


def get_currency_details(
    currency_code: str,
    url: str = "https://www.cbr-xml-daily.ru/daily_json.js"
) -> Optional[Dict[str, Any]]:
    """
    Получить подробную информацию о валюте.
    
    Args:
        currency_code: Код валюты (например, 'USD')
        url: URL API ЦБ РФ
    
    Returns:
        Словарь с детальной информацией о валюте или None, если валюта не найдена
    """
    try:
        currencies = get_currencies([currency_code], url)
        
        if currency_code not in currencies:
            return None
        
        # Получаем полные данные
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'Valute' not in data or currency_code not in data['Valute']:
            return None
        
        currency_data = data['Valute'][currency_code]
        
        return {
            'id': currency_data.get('ID', ''),
            'num_code': currency_data.get('NumCode', ''),
            'char_code': currency_data.get('CharCode', ''),
            'nominal': currency_data.get('Nominal', 1),
            'name': currency_data.get('Name', ''),
            'value': float(str(currency_data.get('Value', 0)).replace(',', '.')),
            'previous': float(str(currency_data.get('Previous', 0)).replace(',', '.')),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception:
        return None


def get_all_currencies(
    url: str = "https://www.cbr-xml-daily.ru/daily_json.js"
) -> List[Dict[str, Any]]:
    """
    Получить информацию обо всех доступных валютах.
    
    Args:
        url: URL API ЦБ РФ
    
    Returns:
        Список словарей с информацией о валютах
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'Valute' not in data:
            return []
        
        result = []
        for code, currency_data in data['Valute'].items():
            try:
                currency_info = {
                    'id': currency_data.get('ID', ''),
                    'num_code': currency_data.get('NumCode', ''),
                    'char_code': currency_data.get('CharCode', ''),
                    'nominal': currency_data.get('Nominal', 1),
                    'name': currency_data.get('Name', ''),
                    'value': float(str(currency_data.get('Value', 0)).replace(',', '.')),
                    'previous': float(str(currency_data.get('Previous', 0)).replace(',', '.')),
                    'timestamp': datetime.now().isoformat()
                }
                result.append(currency_info)
            except (ValueError, TypeError):
                continue
        
        return result
        
    except Exception:
        return []


def calculate_exchange(
    amount: float,
    from_currency: str,
    to_currency: str = "RUB",
    url: str = "https://www.cbr-xml-daily.ru/daily_json.js"
) -> Optional[float]:
    """
    Рассчитать обмен валют.
    
    Args:
        amount: Сумма для обмена
        from_currency: Исходная валюта
        to_currency: Целевая валюта (по умолчанию RUB)
        url: URL API ЦБ РФ
    
    Returns:
        Сумма в целевой валюте или None в случае ошибки
    """
    try:
        # Если обе валюты одинаковые
        if from_currency == to_currency:
            return amount
        
        # Получаем курсы
        if to_currency == "RUB":
            # Прямой расчет в рубли
            currencies = get_currencies([from_currency], url)
            if from_currency not in currencies:
                return None
            return amount * currencies[from_currency]
        
        elif from_currency == "RUB":
            # Расчет из рублей
            currencies = get_currencies([to_currency], url)
            if to_currency not in currencies:
                return None
            return amount / currencies[to_currency]
        
        else:
            # Кросс-курс через рубли
            currencies = get_currencies([from_currency, to_currency], url)
            if from_currency not in currencies or to_currency not in currencies:
                return None
            
            # Конвертируем в рубли, затем в целевую валюту
            amount_in_rub = amount * currencies[from_currency]
            return amount_in_rub / currencies[to_currency]
            
    except Exception:
        return None


def get_currency_history(
    currency_code: str,
    days: int = 30,
    base_url: str = "https://www.cbr-xml-daily.ru"
) -> List[Dict[str, Any]]:
    """
    Получить историю курса валюты за указанное количество дней.
    
    Args:
        currency_code: Код валюты
        days: Количество дней истории
        base_url: Базовый URL API ЦБ РФ
    
    Returns:
        Список словарей с историческими данными
    """
    history = []
    
    try:
        # Получаем текущий курс
        current_data = get_currency_details(currency_code, base_url + "/daily_json.js")
        if current_data:
            history.append({
                'date': datetime.now().date().isoformat(),
                'value': current_data['value'],
                'nominal': current_data['nominal']
            })
        
        # Получаем исторические данные (симуляция)
        # В реальном приложении здесь был бы запрос к API исторических данных
        for i in range(1, min(days, 30)):
            # Генерируем тестовые данные
            date = (datetime.now() - timedelta(days=i)).date()
            
            # Симулируем изменение курса
            if current_data:
                base_value = current_data['value']
                # Небольшие случайные колебания
                import random
                change = random.uniform(-0.02, 0.02) * base_value
                historical_value = base_value + change
                
                history.append({
                    'date': date.isoformat(),
                    'value': historical_value,
                    'nominal': current_data['nominal']
                })
        
        # Сортируем по дате
        history.sort(key=lambda x: x['date'])
        
    except Exception:
        pass
    
    return history


if __name__ == "__main__":
    # Тестирование модуля
    print("Тестирование модуля currencies_api...")
    
    try:
        # Тест 1: Получение курсов основных валют
        print("\n1. Получение курсов USD и EUR:")
        rates = get_currencies(['USD', 'EUR'])
        for code, rate in rates.items():
            print(f"  {code}: {rate} RUB")
        
        # Тест 2: Получение детальной информации
        print("\n2. Детальная информация о USD:")
        details = get_currency_details('USD')
        if details:
            for key, value in details.items():
                print(f"  {key}: {value}")
        
        # Тест 3: Расчет обмена
        print("\n3. Расчет обмена 100 USD в RUB:")
        result = calculate_exchange(100, 'USD', 'RUB')
        if result:
            print(f"  Результат: {result:.2f} RUB")
        
        # Тест 4: Получение всех валют
        print("\n4. Все доступные валюты:")
        all_currencies = get_all_currencies()
        print(f"  Найдено валют: {len(all_currencies)}")
        
    except Exception as e:
        print(f"Ошибка при тестировании: {e}")