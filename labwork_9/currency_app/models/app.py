"""
Модель приложения.

Содержит информацию о приложении: название, версию и автора.
"""

from typing import Any
from .author import Author


class App:
    """Класс, представляющий приложение."""
    
    def __init__(self, name: str, version: str, author: Author) -> None:
        """
        Инициализация объекта приложения.
        
        Args:
            name: Название приложения
            version: Версия приложения
            author: Объект автора приложения
        """
        self._name = name
        self._version = version
        self._author = author
    
    @property
    def name(self) -> str:
        """Получить название приложения."""
        return self._name
    
    @name.setter
    def name(self, value: str) -> None:
        """Установить название приложения."""
        if not isinstance(value, str):
            raise TypeError("Название должно быть строкой")
        if not value.strip():
            raise ValueError("Название не может быть пустым")
        self._name = value.strip()
    
    @property
    def version(self) -> str:
        """Получить версию приложения."""
        return self._version
    
    @version.setter
    def version(self, value: str) -> None:
        """Установить версию приложения."""
        if not isinstance(value, str):
            raise TypeError("Версия должна быть строкой")
        # Простая валидация версии (формат X.Y.Z)
        parts = value.split('.')
        if len(parts) != 3:
            raise ValueError("Версия должна быть в формате X.Y.Z")
        for part in parts:
            if not part.isdigit():
                raise ValueError("Все части версии должны быть числами")
        self._version = value
    
    @property
    def author(self) -> Author:
        """Получить автора приложения."""
        return self._author
    
    @author.setter
    def author(self, value: Author) -> None:
        """Установить автора приложения."""
        if not isinstance(value, Author):
            raise TypeError("Автор должен быть объектом класса Author")
        self._author = value
    
    def to_dict(self) -> dict[str, Any]:
        """
        Преобразовать объект в словарь.
        
        Returns:
            Словарь с данными приложения
        """
        return {
            'name': self.name,
            'version': self.version,
            'author': self.author.to_dict()
        }
    
    def __repr__(self) -> str:
        """Строковое представление объекта."""
        return f"App(name='{self.name}', version='{self.version}', author={repr(self.author)})"
    
    def __str__(self) -> str:
        """Пользовательское строковое представление."""
        return f"{self.name} v{self.version} by {self.author}"