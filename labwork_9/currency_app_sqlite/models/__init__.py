"""
Пакет моделей для приложения отслеживания курсов валют.

Этот пакет содержит все модели предметной области:
- Author - автор приложения
- App - информация о приложении
- User - пользователь системы
- Currency - валюта
- UserCurrency - связь пользователя с валютой
"""

from .author import Author
from .app import App
from .user import User
from .currency import Currency
from .user_currency import UserCurrency

__all__ = ['Author', 'App', 'User', 'Currency', 'UserCurrency']