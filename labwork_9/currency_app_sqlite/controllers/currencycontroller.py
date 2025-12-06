"""
Контроллер для бизнес-логики работы с валютами.
Использует DatabaseController для работы с базой данных.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from controllers.databasecontroller import CurrencyRatesCRUD


class CurrencyController:
    """Контроллер для работы с валютами."""
    
    def __init__(self, db_controller: CurrencyRatesCRUD):
        """
        Инициализация контроллера валют.
        
        Args:
            db_controller: Контроллер CRUD операций с валютами
        """
        self.db = db_controller
    
    def list_currencies(self) -> List[Dict[str, Any]]:
        """
        Получить список всех валют.
        
        Returns:
            Список словарей с информацией о валютах
        """
        return self.db._read()
    
    def get_currency(self, currency_id: int) -> Optional[Dict[str, Any]]:
        """
        Получить информацию о валюте по ID.
        
        Args:
            currency_id: ID валюты
        
        Returns:
            Словарь с информацией о валюте или None
        """
        result = self.db._read()
        for currency in result:
            if currency['id'] == currency_id:
                return currency
        return None
    
    def update_currency(self, char_code: str, value: float) -> bool:
        """
        Обновить курс валюты.
        
        Args:
            char_code: Символьный код валюты
            value: Новое значение курса
        
        Returns:
            True если обновление успешно, False в противном случае
        """
        return self.db._update({char_code: value})
    
    def delete_currency(self, currency_id: int) -> bool:
        """
        Удалить валюту.
        
        Args:
            currency_id: ID валюты
        
        Returns:
            True если удаление успешно, False в противном случае
        """
        return self.db._delete(currency_id)
    
    def add_currency(self, num_code: str, char_code: str, name: str, 
                    value: float, nominal: int) -> bool:
        """
        Добавить новую валюту.
        
        Args:
            num_code: Цифровой код
            char_code: Символьный код
            name: Название валюты
            value: Курс
            nominal: Номинал
        
        Returns:
            True если добавление успешно, False в противном случае
        """
        currencies = [{
            'num_code': num_code,
            'char_code': char_code,
            'name': name,
            'value': value,
            'nominal': nominal
        }]
        
        return self.db._create(currencies)
    
    def get_currencies_for_user(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Получить список валют для конкретного пользователя.
        
        Args:
            user_id: ID пользователя
        
        Returns:
            Список словарей с информацией о валютах пользователя
        """
        # В реальном приложении здесь бы вызывался метод DatabaseController
        # Для примера возвращаем все валюты
        all_currencies = self.list_currencies()
        
        # Отмечаем, подписан ли пользователь на каждую валюту
        # В реальном приложении это бы делалось через JOIN в SQL
        for currency in all_currencies:
            currency['is_subscribed'] = self._is_user_subscribed(user_id, currency['id'])
        
        return all_currencies
    
    def _is_user_subscribed(self, user_id: int, currency_id: int) -> bool:
        """
        Проверить, подписан ли пользователь на валюту.
        
        Args:
            user_id: ID пользователя
            currency_id: ID валюты
        
        Returns:
            True если подписан, False в противном случае
        """
        # В реальном приложении здесь бы был запрос к БД
        # Для примера возвращаем фиктивное значение
        return False
    
    def format_currency_value(self, value: float, nominal: int) -> str:
        """
        Форматировать значение курса валюты.
        
        Args:
            value: Курс валюты
            nominal: Номинал
        
        Returns:
            Отформатированная строка
        """
        value_per_unit = value / nominal
        return f"{value_per_unit:.4f}"
    
    def get_currency_stats(self) -> Dict[str, Any]:
        """
        Получить статистику по валютам.
        
        Returns:
            Словарь со статистикой
        """
        currencies = self.list_currencies()
        
        if not currencies:
            return {}
        
        # Находим валюту с максимальным и минимальным курсом
        max_currency = max(currencies, key=lambda x: x['value'])
        min_currency = min(currencies, key=lambda x: x['value'])
        
        # Вычисляем средний курс
        total_value = sum(c['value'] for c in currencies)
        avg_value = total_value / len(currencies)
        
        return {
            'total_count': len(currencies),
            'max_value': {
                'char_code': max_currency['char_code'],
                'value': max_currency['value'],
                'name': max_currency['name']
            },
            'min_value': {
                'char_code': min_currency['char_code'],
                'value': min_currency['value'],
                'name': min_currency['name']
            },
            'avg_value': avg_value,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }