"""
Контроллер для рендеринга HTML страниц через Jinja2.
"""

from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape
from controllers.databasecontroller import DatabaseController
from controllers.currencycontroller import CurrencyController


class PagesController:
    """Контроллер для рендеринга страниц."""
    
    def __init__(self, template_dir: str = "templates"):
        """
        Инициализация контроллера страниц.
        
        Args:
            template_dir: Директория с шаблонами
        """
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def render_index(self, db: DatabaseController) -> str:
        """
        Рендерить главную страницу.
        
        Args:
            db: Контроллер базы данных
        
        Returns:
            HTML содержимое страницы
        """
        template = self.env.get_template('index.html')
        
        # Получаем информацию о приложении
        app_info = db.get_app_info()
        
        # Получаем статистику
        stats = db.get_statistics()
        
        # Получаем последние валюты
        currencies = db.read_currency()[:5]  # Последние 5 валют
        
        context = {
            'app_name': app_info.get('app_name', 'Currency Tracker'),
            'app_version': app_info.get('app_version', '1.0.0'),
            'author_name': app_info.get('author_name', 'Иван Иванов'),
            'author_group': app_info.get('author_group', 'ПИ-202'),
            'user_count': stats.get('user_count', 0),
            'currency_count': stats.get('currency_count', 0),
            'subscription_count': stats.get('subscription_count', 0),
            'last_update': stats.get('last_update', 'Неизвестно'),
            'currencies': currencies
        }
        
        return template.render(**context)
    
    def render_currencies(self, db: DatabaseController, 
                         currency_controller: CurrencyController) -> str:
        """
        Рендерить страницу со списком валют.
        
        Args:
            db: Контроллер базы данных
            currency_controller: Контроллер валют
        
        Returns:
            HTML содержимое страницы
        """
        template = self.env.get_template('currencies.html')
        
        # Получаем все валюты
        currencies = currency_controller.list_currencies()
        
        # Получаем статистику
        stats = currency_controller.get_currency_stats()
        
        # Получаем информацию о приложении
        app_info = db.get_app_info()
        
        context = {
            'currencies': currencies,
            'stats': stats,
            'app_name': app_info.get('app_name', 'Currency Tracker'),
            'app_version': app_info.get('app_version', '1.0.0'),
            'author_name': app_info.get('author_name', 'Иван Иванов'),
            'author_group': app_info.get('author_group', 'ПИ-202')
        }
        
        return template.render(**context)
    
    def render_users(self, db: DatabaseController) -> str:
        """
        Рендерить страницу со списком пользователей.
        
        Args:
            db: Контроллер базы данных
        
        Returns:
            HTML содержимое страницы
        """
        template = self.env.get_template('users.html')
        
        # Получаем всех пользователей
        users = db.read_user()
        
        # Получаем информацию о приложении
        app_info = db.get_app_info()
        
        context = {
            'users': users,
            'app_name': app_info.get('app_name', 'Currency Tracker'),
            'app_version': app_info.get('app_version', '1.0.0'),
            'author_name': app_info.get('author_name', 'Иван Иванов'),
            'author_group': app_info.get('author_group', 'ПИ-202')
        }
        
        return template.render(**context)
    
    def render_user(self, db: DatabaseController, user_id: int) -> str:
        """
        Рендерить страницу пользователя.
        
        Args:
            db: Контроллер базы данных
            user_id: ID пользователя
        
        Returns:
            HTML содержимое страницы
        """
        template = self.env.get_template('user.html')
        
        # Получаем информацию о пользователе
        users = db.read_user(user_id)
        
        if not users:
            # Пользователь не найден
            error_template = self.env.get_template('error.html')
            return error_template.render(
                error_code=404,
                error_message="Пользователь не найден"
            )
        
        user = users[0]
        
        # Получаем подписки пользователя
        subscriptions = db.get_user_subscriptions(user_id)
        
        # Получаем информацию о приложении
        app_info = db.get_app_info()
        
        context = {
            'user': user,
            'subscriptions': subscriptions,
            'app_name': app_info.get('app_name', 'Currency Tracker'),
            'app_version': app_info.get('app_version', '1.0.0'),
            'author_name': app_info.get('author_name', 'Иван Иванов'),
            'author_group': app_info.get('author_group', 'ПИ-202')
        }
        
        return template.render(**context)
    
    def render_author(self, db: DatabaseController) -> str:
        """
        Рендерить страницу об авторе.
        
        Args:
            db: Контроллер базы данных
        
        Returns:
            HTML содержимое страницы
        """
        template = self.env.get_template('author.html')
        
        # Получаем информацию о приложении и авторе
        app_info = db.get_app_info()
        
        context = {
            'app_name': app_info.get('app_name', 'Currency Tracker'),
            'app_version': app_info.get('app_version', '1.0.0'),
            'author_name': app_info.get('author_name', 'Иван Иванов'),
            'author_group': app_info.get('author_group', 'ПИ-202'),
            'lines_of_code': 1500,  # Примерные значения
            'files_count': 25,
            'models_count': 5,
            'templates_count': 5
        }
        
        return template.render(**context)
    
    def render_error(self, error_code: int, error_message: str) -> str:
        """
        Рендерить страницу ошибки.
        
        Args:
            error_code: Код ошибки
            error_message: Сообщение об ошибке
        
        Returns:
            HTML содержимое страницы
        """
        template = self.env.get_template('error.html')
        
        context = {
            'error_code': error_code,
            'error_message': error_message
        }
        
        return template.render(**context)