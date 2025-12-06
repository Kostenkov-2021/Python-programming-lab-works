"""
Модель пользователя.

Содержит информацию о пользователе системы и его подписках на валюты.
"""

from typing import Any, List, Optional
from .user_currency import UserCurrency


class User:
    """Класс, представляющий пользователя системы."""
    
    def __init__(self, user_id: int, name: str) -> None:
        """
        Инициализация объекта пользователя.
        
        Args:
            user_id: Уникальный идентификатор пользователя
            name: Имя пользователя
        """
        self._id = user_id
        self._name = name
        self._subscriptions: List[UserCurrency] = []
    
    @property
    def id(self) -> int:
        """Получить идентификатор пользователя."""
        return self._id
    
    @id.setter
    def id(self, value: int) -> None:
        """Установить идентификатор пользователя."""
        if not isinstance(value, int):
            raise TypeError("ID должен быть целым числом")
        if value <= 0:
            raise ValueError("ID должен быть положительным числом")
        self._id = value
    
    @property
    def name(self) -> str:
        """Получить имя пользователя."""
        return self._name
    
    @name.setter
    def name(self, value: str) -> None:
        """Установить имя пользователя."""
        if not isinstance(value, str):
            raise TypeError("Имя должно быть строкой")
        if not value.strip():
            raise ValueError("Имя не может быть пустым")
        self._name = value.strip()
    
    @property
    def subscriptions(self) -> List[UserCurrency]:
        """Получить список подписок пользователя."""
        return self._subscriptions.copy()
    
    def subscribe_to_currency(self, currency_id: str) -> UserCurrency:
        """
        Добавить подписку на валюту.
        
        Args:
            currency_id: ID валюты для подписки
        
        Returns:
            Созданный объект UserCurrency
        
        Raises:
            ValueError: Если пользователь уже подписан на эту валюту
        """
        # Проверяем, не подписан ли уже пользователь
        if any(sub.currency_id == currency_id for sub in self._subscriptions):
            raise ValueError(f"Пользователь уже подписан на валюту {currency_id}")
        
        # Создаем новую подписку
        subscription_id = len(self._subscriptions) + 1
        subscription = UserCurrency(subscription_id, self.id, currency_id)
        self._subscriptions.append(subscription)
        
        return subscription
    
    def unsubscribe_from_currency(self, currency_id: str) -> bool:
        """
        Удалить подписку на валюту.
        
        Args:
            currency_id: ID валюты для отписки
        
        Returns:
            True если подписка удалена, False если не найдена
        """
        initial_length = len(self._subscriptions)
        self._subscriptions = [
            sub for sub in self._subscriptions 
            if sub.currency_id != currency_id
        ]
        return len(self._subscriptions) < initial_length
    
    def get_subscribed_currency_ids(self) -> List[str]:
        """
        Получить список ID валют, на которые подписан пользователь.
        
        Returns:
            Список ID валют
        """
        return [sub.currency_id for sub in self._subscriptions]
    
    def has_subscription(self, currency_id: str) -> bool:
        """
        Проверить, подписан ли пользователь на указанную валюту.
        
        Args:
            currency_id: ID валюты для проверки
        
        Returns:
            True если подписан, False если нет
        """
        return any(sub.currency_id == currency_id for sub in self._subscriptions)
    
    def to_dict(self, include_subscriptions: bool = True) -> dict[str, Any]:
        """
        Преобразовать объект в словарь.
        
        Args:
            include_subscriptions: Включать ли информацию о подписках
        
        Returns:
            Словарь с данными пользователя
        """
        result = {
            'id': self.id,
            'name': self.name
        }
        
        if include_subscriptions:
            result['subscriptions'] = [
                sub.to_dict() for sub in self._subscriptions
            ]
            result['subscribed_currencies'] = self.get_subscribed_currency_ids()
        
        return result
    
    def __repr__(self) -> str:
        """Строковое представление объекта."""
        return f"User(id={self.id}, name='{self.name}', subscriptions={len(self._subscriptions)})"
    
    def __str__(self) -> str:
        """Пользовательское строковое представление."""
        return f"Пользователь #{self.id}: {self.name}"