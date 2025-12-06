"""
Модель автора приложения.

Содержит информацию об авторе: имя и учебную группу.
"""

from typing import Any


class Author:
    """Класс, представляющий автора приложения."""
    
    def __init__(self, name: str, group: str) -> None:
        """
        Инициализация объекта автора.
        
        Args:
            name: Имя автора
            group: Учебная группа автора
        """
        self._name = name
        self._group = group
    
    @property
    def name(self) -> str:
        """Получить имя автора."""
        return self._name
    
    @name.setter
    def name(self, value: str) -> None:
        """Установить имя автора."""
        if not isinstance(value, str):
            raise TypeError("Имя должно быть строкой")
        if not value.strip():
            raise ValueError("Имя не может быть пустым")
        self._name = value.strip()
    
    @property
    def group(self) -> str:
        """Получить учебную группу автора."""
        return self._group
    
    @group.setter
    def group(self, value: str) -> None:
        """Установить учебную группу автора."""
        if not isinstance(value, str):
            raise TypeError("Группа должна быть строкой")
        if not value.strip():
            raise ValueError("Группа не может быть пустой")
        self._group = value.strip()
    
    def to_dict(self) -> dict[str, Any]:
        """
        Преобразовать объект в словарь.
        
        Returns:
            Словарь с данными автора
        """
        return {
            'name': self.name,
            'group': self.group
        }
    
    def __repr__(self) -> str:
        """Строковое представление объекта."""
        return f"Author(name='{self.name}', group='{self.group}')"
    
    def __str__(self) -> str:
        """Пользовательское строковое представление."""
        return f"{self.name} ({self.group})"