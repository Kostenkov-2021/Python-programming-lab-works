"""
Модель связи пользователя с валютой.

Реализует отношение "многие ко многим" между пользователями и валютами.
"""

from typing import Any


class UserCurrency:
    """Класс, представляющий подписку пользователя на валюту."""
    
    def __init__(self, uc_id: int, user_id: int, currency_id: str) -> None:
        """
        Инициализация объекта подписки.
        
        Args:
            uc_id: Уникальный идентификатор подписки
            user_id: ID пользователя
            currency_id: ID валюты
        """
        self._id = uc_id
        self._user_id = user_id
        self._currency_id = currency_id
    
    @property
    def id(self) -> int:
        """Получить ID подписки."""
        return self._id
    
    @id.setter
    def id(self, value: int) -> None:
        """Установить ID подписки."""
        if not isinstance(value, int):
            raise TypeError("ID подписки должен быть целым числом")
        if value <= 0:
            raise ValueError("ID подписки должен быть положительным числом")
        self._id = value
    
    @property
    def user_id(self) -> int:
        """Получить ID пользователя."""
        return self._user_id
    
    @user_id.setter
    def user_id(self, value: int) -> None:
        """Установить ID пользователя."""
        if not isinstance(value, int):
            raise TypeError("ID пользователя должен быть целым числом")
        if value <= 0:
            raise ValueError("ID пользователя должен быть положительным числом")
        self._user_id = value
    
    @property
    def currency_id(self) -> str:
        """Получить ID валюты."""
        return self._currency_id
    
    @currency_id.setter
    def currency_id(self, value: str) -> None:
        """Установить ID валюты."""
        if not isinstance(value, str):
            raise TypeError("ID валюты должен быть строкой")
        if not value.strip():
            raise ValueError("ID валюты не может быть пустым")
        self._currency_id = value.strip()
    
    def to_dict(self) -> dict[str, Any]:
        """
        Преобразовать объект в словарь.
        
        Returns:
            Словарь с данными подписки
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'currency_id': self.currency_id
        }
    
    def __repr__(self) -> str:
        """Строковое представление объекта."""
        return f"UserCurrency(id={self.id}, user_id={self.user_id}, currency_id='{self.currency_id}')"
    
    def __str__(self) -> str:
        """Пользовательское строковое представление."""
        return f"Подписка #{self.id}: пользователь {self.user_id} → валюта {self.currency_id}"