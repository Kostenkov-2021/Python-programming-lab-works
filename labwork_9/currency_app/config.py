"""
Конфигурационный файл приложения.

Содержит настройки сервера, базы данных и другие параметры приложения.
"""

import os
from typing import Dict, Any
from datetime import timedelta


class Config:
    """Класс конфигурации приложения."""
    
    # Основные настройки
    APP_NAME = "Currency Tracker"
    APP_VERSION = "1.0.0"
    
    # Настройки сервера
    SERVER_HOST = "localhost"
    SERVER_PORT = 8080
    DEBUG = True
    
    # Настройки автора
    AUTHOR_NAME = "Иван Иванов"
    AUTHOR_GROUP = "ПИ-202"
    
    # Настройки API курсов валют
    CURRENCY_API_URL = "https://www.cbr-xml-daily.ru/daily_json.js"
    CURRENCY_API_TIMEOUT = 10.0
    CURRENCY_UPDATE_INTERVAL = timedelta(minutes=5)
    
    # Настройки кэширования
    CACHE_ENABLED = True
    CACHE_TTL = 300  # 5 минут в секундах
    
    # Настройки сессии
    SESSION_TIMEOUT = timedelta(hours=1)
    
    # Настройки базы данных (в памяти для простоты)
    DATABASE = {
        'type': 'in-memory',
        'users': [],
        'currencies': [],
        'subscriptions': []
    }
    
    # Настройки безопасности
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Настройки логирования
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
                'level': 'INFO'
            },
            'file': {
                'class': 'logging.FileHandler',
                'filename': 'currency_tracker.log',
                'formatter': 'standard',
                'level': 'DEBUG'
            }
        },
        'loggers': {
            '': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
                'propagate': True
            }
        }
    }
    
    # Настройки шаблонов
    TEMPLATE_SETTINGS = {
        'autoescape': True,
        'trim_blocks': True,
        'lstrip_blocks': True
    }
    
    # Начальные данные
    INITIAL_USERS = [
        {'id': 1, 'name': 'Иван Иванов'},
        {'id': 2, 'name': 'Мария Петрова'},
        {'id': 3, 'name': 'Алексей Сидоров'}
    ]
    
    INITIAL_CURRENCIES = [
        {
            'id': 'R01235',
            'num_code': '840',
            'char_code': 'USD',
            'name': 'Доллар США',
            'value': 93.25,
            'nominal': 1
        },
        {
            'id': 'R01239',
            'num_code': '978',
            'char_code': 'EUR',
            'name': 'Евро',
            'value': 101.70,
            'nominal': 1
        },
        {
            'id': 'R01035',
            'num_code': '826',
            'char_code': 'GBP',
            'name': 'Фунт стерлингов',
            'value': 118.45,
            'nominal': 1
        },
        {
            'id': 'R01375',
            'num_code': '156',
            'char_code': 'CNY',
            'name': 'Китайский юань',
            'value': 12.89,
            'nominal': 1
        },
        {
            'id': 'R01820',
            'num_code': '392',
            'char_code': 'JPY',
            'name': 'Японская иена',
            'value': 0.63,
            'nominal': 100
        }
    ]
    
    INITIAL_SUBSCRIPTIONS = [
        {'id': 1, 'user_id': 1, 'currency_id': 'R01235'},  # Иван подписан на USD
        {'id': 2, 'user_id': 1, 'currency_id': 'R01239'},  # Иван подписан на EUR
        {'id': 3, 'user_id': 2, 'currency_id': 'R01239'},  # Мария подписан на EUR
        {'id': 4, 'user_id': 3, 'currency_id': 'R01035'},  # Алексей подписан на GBP
    ]
    
    @classmethod
    def get_database_config(cls) -> Dict[str, Any]:
        """Получить конфигурацию базы данных."""
        return cls.DATABASE
    
    @classmethod
    def get_logging_config(cls) -> Dict[str, Any]:
        """Получить конфигурацию логирования."""
        return cls.LOGGING
    
    @classmethod
    def get_template_settings(cls) -> Dict[str, Any]:
        """Получить настройки шаблонов."""
        return cls.TEMPLATE_SETTINGS
    
    @classmethod
    def get_author_info(cls) -> Dict[str, str]:
        """Получить информацию об авторе."""
        return {
            'name': cls.AUTHOR_NAME,
            'group': cls.AUTHOR_GROUP
        }
    
    @classmethod
    def get_app_info(cls) -> Dict[str, str]:
        """Получить информацию о приложении."""
        return {
            'name': cls.APP_NAME,
            'version': cls.APP_VERSION,
            'author': cls.get_author_info()
        }


class DevelopmentConfig(Config):
    """Конфигурация для разработки."""
    DEBUG = True
    SERVER_HOST = "localhost"
    SERVER_PORT = 8080


class ProductionConfig(Config):
    """Конфигурация для продакшена."""
    DEBUG = False
    SERVER_HOST = "0.0.0.0"
    SERVER_PORT = 80
    SECRET_KEY = os.environ.get('SECRET_KEY', 'production-secret-key')


# Выбор конфигурации в зависимости от окружения
def get_config() -> Config:
    """Получить конфигурацию в зависимости от окружения."""
    env = os.environ.get('APP_ENV', 'development').lower()
    
    if env == 'production':
        return ProductionConfig
    else:
        return DevelopmentConfig


# Текущая конфигурация
current_config = get_config()