"""
Модель валюты.

Содержит информацию о валюте: код, название, курс и номинал.
"""

from typing import Any
from datetime import datetime


class Currency:
    """Класс, представляющий валюту."""
    
    def __init__(
        self,
        currency_id: str,
        num_code: str,
        char_code: str,
        name: str,
        value: float,
        nominal: int,
        last_updated: Optional[datetime] = None
    ) -> None:
        """
        Инициализация объекта валюты.
        
        Args:
            currency_id: Уникальный идентификатор валюты
            num_code: Цифровой код валюты
            char_code: Символьный код валюты
            name: Название валюты
            value: Курс валюты к рублю
            nominal: Номинал (за сколько единиц указан курс)
            last_updated: Время последнего обновления курса
        """
        self._id = currency_id
        self._num_code = num_code
        self._char_code = char_code
        self._name = name
        self._value = value
        self._nominal = nominal
        self._last_updated = last_updated or datetime.now()
    
    @property
    def id(self) -> str:
        """Получить ID валюты."""
        return self._id
    
    @id.setter
    def id(self, value: str) -> None:
        """Установить ID валюты."""
        if not isinstance(value, str):
            raise TypeError("ID валюты должен быть строкой")
        if not value.strip():
            raise ValueError("ID валюты не может быть пустым")
        self._id = value.strip()
    
    @property
    def num_code(self) -> str:
        """Получить цифровой код валюты."""
        return self._num_code
    
    @num_code.setter
    def num_code(self, value: str) -> None:
        """Установить цифровой код валюты."""
        if not isinstance(value, str):
            raise TypeError("Цифровой код должен быть строкой")
        if not value.isdigit():
            raise ValueError("Цифровой код должен содержать только цифры")
        if len(value) != 3:
            raise ValueError("Цифровой код должен состоять из 3 цифр")
        self._num_code = value
    
    @property
    def char_code(self) -> str:
        """Получить символьный код валюты."""
        return self._char_code
    
    @char_code.setter
    def char_code(self, value: str) -> None:
        """Установить символьный код валюты."""
        if not isinstance(value, str):
            raise TypeError("Символьный код должен быть строкой")
        if len(value) != 3:
            raise ValueError("Символьный код должен состоять из 3 символов")
        self._char_code = value.upper()
    
    @property
    def name(self) -> str:
        """Получить название валюты."""
        return self._name
    
    @name.setter
    def name(self, value: str) -> None:
        """Установить название валюты."""
        if not isinstance(value, str):
            raise TypeError("Название должно быть строкой")
        if not value.strip():
            raise ValueError("Название не может быть пустым")
        self._name = value.strip()
    
    @property
    def value(self) -> float:
        """Получить курс валюты."""
        return self._value
    
    @value.setter
    def value(self, value: float) -> None:
        """Установить курс валюты."""
        if not isinstance(value, (int, float)):
            raise TypeError("Курс должен быть числом")
        if value <= 0:
            raise ValueError("Курс должен быть положительным числом")
        self._value = float(value)
    
    @property
    def nominal(self) -> int:
        """Получить номинал валюты."""
        return self._nominal
    
    @nominal.setter
    def nominal(self, value: int) -> None:
        """Установить номинал валюты."""
        if not isinstance(value, int):
            raise TypeError("Номинал должен быть целым числом")
        if value <= 0:
            raise ValueError("Номинал должен быть положительным числом")
        self._nominal = value
    
    @property
    def last_updated(self) -> datetime:
        """Получить время последнего обновления."""
        return self._last_updated
    
    @last_updated.setter
    def last_updated(self, value: datetime) -> None:
        """Установить время последнего обновления."""
        if not isinstance(value, datetime):
            raise TypeError("Время обновления должно быть объектом datetime")
        self._last_updated = value
    
    def get_value_for_nominal(self, custom_nominal: int = 1) -> float:
        """
        Получить курс для произвольного номинала.
        
        Args:
            custom_nominal: Желаемый номинал
        
        Returns:
            Курс для указанного номинала
        """
        if custom_nominal <= 0:
            raise ValueError("Номинал должен быть положительным числом")
        return (self._value / self._nominal) * custom_nominal
    
    def to_dict(self) -> dict[str, Any]:
        """
        Преобразовать объект в словарь.
        
        Returns:
            Словарь с данными валюты
        """
        return {
            'id': self.id,
            'num_code': self.num_code,
            'char_code': self.char_code,
            'name': self.name,
            'value': self.value,
            'nominal': self.nominal,
            'last_updated': self.last_updated.isoformat(),
            'value_per_unit': self.get_value_for_nominal(1)
        }
    
    def __repr__(self) -> str:
        """Строковое представление объекта."""
        return f"Currency(id='{self.id}', char_code='{self.char_code}', name='{self.name}', value={self.value})"
    
    def __str__(self) -> str:
        """Пользовательское строковое представление."""
        return f"{self.char_code} ({self.name}): {self.value} RUB за {self.nominal}"