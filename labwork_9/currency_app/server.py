"""
Основной серверный модуль приложения Currency Tracker.

Реализует HTTP-сервер с маршрутизацией, обработкой запросов и рендерингом шаблонов.
"""

import json
import os
import sys
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, unquote
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass

# Добавляем текущую директорию в путь для импорта модулей
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Импортируем Jinja2
from jinja2 import Environment, FileSystemLoader, select_autoescape

# Импортируем модели
from models import Author, App, User, Currency, UserCurrency

# Импортируем утилиты
from utils.currencies_api import (
    get_currencies, 
    get_currency_details, 
    get_all_currencies,
    calculate_exchange,
    get_currency_history
)

# Импортируем конфигурацию
from config import current_config as config


# Настройка логирования
logging.basicConfig(
    level=logging.INFO if config.DEBUG else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class RequestContext:
    """Контекст HTTP-запроса."""
    path: str
    query_params: Dict[str, List[str]]
    method: str
    headers: Dict[str, str]
    body: Optional[bytes] = None
    
    def get_first_param(self, name: str, default: Any = None) -> Any:
        """Получить первый параметр запроса."""
        if name in self.query_params and self.query_params[name]:
            return self.query_params[name][0]
        return default
    
    def get_json_body(self) -> Optional[Dict[str, Any]]:
        """Получить тело запроса как JSON."""
        if self.body:
            try:
                return json.loads(self.body.decode('utf-8'))
            except json.JSONDecodeError:
                return None
        return None


class CurrencyTrackerServer(BaseHTTPRequestHandler):
    """HTTP-сервер приложения Currency Tracker."""
    
    # Инициализация Jinja2
    env = Environment(
        loader=FileSystemLoader('templates'),
        autoescape=select_autoescape(['html', 'xml']),
        trim_blocks=True,
        lstrip_blocks=True
    )
    
    # Состояние приложения
    app_data = {
        'app': App(
            name=config.APP_NAME,
            version=config.APP_VERSION,
            author=Author(
                name=config.AUTHOR_NAME,
                group=config.AUTHOR_GROUP
            )
        ),
        'users': [],
        'currencies': [],
        'subscriptions': [],
        'last_currency_update': None
    }
    
    # Текущий пользователь (для простоты используем первого)
    current_user_id = 1
    
    def __init__(self, *args, **kwargs):
        """Инициализация сервера."""
        self.initialize_app_data()
        super().__init__(*args, **kwargs)
    
    def initialize_app_data(self):
        """Инициализация данных приложения."""
        # Создаем автора и приложение
        author = Author(config.AUTHOR_NAME, config.AUTHOR_GROUP)
        app = App(config.APP_NAME, config.APP_VERSION, author)
        
        # Создаем пользователей
        users = []
        for user_data in config.INITIAL_USERS:
            user = User(user_data['id'], user_data['name'])
            users.append(user)
        
        # Создаем валюты
        currencies = []
        for currency_data in config.INITIAL_CURRENCIES:
            currency = Currency(
                currency_id=currency_data['id'],
                num_code=currency_data['num_code'],
                char_code=currency_data['char_code'],
                name=currency_data['name'],
                value=currency_data['value'],
                nominal=currency_data['nominal'],
                last_updated=datetime.now()
            )
            currencies.append(currency)
        
        # Создаем подписки
        subscriptions = []
        for sub_data in config.INITIAL_SUBSCRIPTIONS:
            # Находим пользователя
            user = next((u for u in users if u.id == sub_data['user_id']), None)
            if user:
                try:
                    subscription = user.subscribe_to_currency(sub_data['currency_id'])
                    subscriptions.append(subscription)
                except ValueError:
                    # Подписка уже существует
                    pass
        
        # Обновляем состояние
        self.app_data.update({
            'app': app,
            'users': users,
            'currencies': currencies,
            'subscriptions': subscriptions,
            'last_currency_update': datetime.now()
        })
    
    def log_request(self, code='-', size='-'):
        """Логирование запросов."""
        if config.DEBUG:
            logger.info(f'{self.command} {self.path} - {code}')
    
    def do_GET(self):
        """Обработка GET-запросов."""
        try:
            # Парсим URL
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            query_params = parse_qs(parsed_url.query)
            
            # Создаем контекст запроса
            context = RequestContext(
                path=path,
                query_params=query_params,
                method='GET',
                headers=dict(self.headers)
            )
            
            # Маршрутизация
            if path == '/':
                self.handle_index(context)
            elif path == '/users':
                self.handle_users(context)
            elif path == '/user':
                self.handle_user(context)
            elif path == '/currencies':
                self.handle_currencies(context)
            elif path == '/author':
                self.handle_author(context)
            elif path.startswith('/static/'):
                self.handle_static(context)
            elif path.startswith('/api/'):
                self.handle_api(context)
            else:
                self.handle_404(context)
                
        except Exception as e:
            logger.error(f"Error processing GET request: {e}")
            self.handle_error(500, str(e))
    
    def do_POST(self):
        """Обработка POST-запросов."""
        try:
            # Читаем тело запроса
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None
            
            # Парсим URL
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            query_params = parse_qs(parsed_url.query)
            
            # Создаем контекст запроса
            context = RequestContext(
                path=path,
                query_params=query_params,
                method='POST',
                headers=dict(self.headers),
                body=body
            )
            
            # Маршрутизация API
            if path.startswith('/api/'):
                self.handle_api(context)
            else:
                self.handle_404(context)
                
        except Exception as e:
            logger.error(f"Error processing POST request: {e}")
            self.handle_error(500, str(e))
    
    def handle_index(self, context: RequestContext):
        """Обработка главной страницы."""
        template = self.env.get_template('index.html')
        
        # Подготавливаем данные для шаблона
        template_data = {
            'app': self.app_data['app'],
            'users_count': len(self.app_data['users']),
            'currencies_count': len(self.app_data['currencies']),
            'subscriptions_count': len(self.app_data['subscriptions']),
            'last_update': self.format_datetime(self.app_data['last_currency_update']),
            'app_version': config.APP_VERSION,
            'author_name': config.AUTHOR_NAME,
            'author_group': config.AUTHOR_GROUP
        }
        
        html_content = template.render(**template_data)
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def handle_users(self, context: RequestContext):
        """Обработка страницы пользователей."""
        template = self.env.get_template('users.html')
        
        # Подготавливаем данные пользователей
        users_data = []
        for user in self.app_data['users']:
            user_dict = user.to_dict()
            users_data.append(user_dict)
        
        template_data = {
            'users': users_data,
            'app_version': config.APP_VERSION,
            'author_name': config.AUTHOR_NAME,
            'author_group': config.AUTHOR_GROUP
        }
        
        html_content = template.render(**template_data)
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def handle_user(self, context: RequestContext):
        """Обработка страницы конкретного пользователя."""
        user_id = context.get_first_param('id')
        
        if not user_id:
            self.handle_error(400, "User ID is required")
            return
        
        try:
            user_id = int(user_id)
            user = next((u for u in self.app_data['users'] if u.id == user_id), None)
            
            if not user:
                self.handle_error(404, "User not found")
                return
            
            # Получаем подписки пользователя
            user_currency_ids = user.get_subscribed_currency_ids()
            subscriptions = [
                c for c in self.app_data['currencies'] 
                if c.id in user_currency_ids
            ]
            
            # Подготавливаем данные для графика
            chart_data = self.generate_chart_data(subscriptions)
            
            template = self.env.get_template('user.html')
            
            template_data = {
                'user': user,
                'subscriptions': subscriptions,
                'all_currencies': self.app_data['currencies'],
                'chart_data': chart_data,
                'app_version': config.APP_VERSION,
                'author_name': config.AUTHOR_NAME,
                'author_group': config.AUTHOR_GROUP
            }
            
            html_content = template.render(**template_data)
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))
            
        except ValueError:
            self.handle_error(400, "Invalid user ID")
    
    def handle_currencies(self, context: RequestContext):
        """Обработка страницы валют."""
        # Проверяем, нужно ли обновить курсы
        refresh = context.get_first_param('refresh')
        if refresh == 'true':
            self.update_currencies_from_api()
        
        template = self.env.get_template('currencies.html')
        
        # Получаем текущего пользователя
        current_user = next(
            (u for u in self.app_data['users'] if u.id == self.current_user_id), 
            None
        )
        
        # Подготавливаем данные валют
        currencies_data = []
        for currency in self.app_data['currencies']:
            currency_dict = currency.to_dict()
            # Форматируем дату для отображения
            currency_dict['last_updated'] = self.format_datetime(currency.last_updated)
            currencies_data.append(currency_dict)
        
        template_data = {
            'currencies': currencies_data,
            'current_user': current_user.to_dict() if current_user else None,
            'last_update': self.format_datetime(self.app_data['last_currency_update']),
            'app_version': config.APP_VERSION,
            'author_name': config.AUTHOR_NAME,
            'author_group': config.AUTHOR_GROUP
        }
        
        html_content = template.render(**template_data)
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def handle_author(self, context: RequestContext):
        """Обработка страницы об авторе."""
        template = self.env.get_template('author.html')
        
        # Подсчитываем статистику проекта
        lines_of_code = self.count_lines_of_code()
        files_count = self.count_project_files()
        
        template_data = {
            'author': self.app_data['app'].author,
            'lines_of_code': lines_of_code,
            'files_count': files_count,
            'models_count': 5,  # Author, App, User, Currency, UserCurrency
            'templates_count': 6,  # Все шаблоны
            'app_version': config.APP_VERSION,
            'author_name': config.AUTHOR_NAME,
            'author_group': config.AUTHOR_GROUP
        }
        
        html_content = template.render(**template_data)
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def handle_static(self, context: RequestContext):
        """Обработка статических файлов."""
        try:
            # Безопасно получаем путь к файлу
            static_path = unquote(context.path)
            
            # Защита от directory traversal
            if '..' in static_path:
                self.handle_error(403, "Access denied")
                return
            
            # Определяем MIME-тип
            mime_types = {
                '.css': 'text/css',
                '.js': 'application/javascript',
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.gif': 'image/gif',
                '.svg': 'image/svg+xml',
                '.ico': 'image/x-icon',
                '.json': 'application/json'
            }
            
            # Полный путь к файлу
            file_path = os.path.join('.', static_path.lstrip('/'))
            
            if not os.path.exists(file_path):
                self.handle_error(404, "File not found")
                return
            
            # Определяем расширение файла
            _, ext = os.path.splitext(file_path)
            content_type = mime_types.get(ext.lower(), 'application/octet-stream')
            
            # Читаем и отправляем файл
            with open(file_path, 'rb') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            
        except Exception as e:
            logger.error(f"Error serving static file: {e}")
            self.handle_error(500, str(e))
    
    def handle_api(self, context: RequestContext):
        """Обработка API запросов."""
        api_path = context.path[4:]  # Убираем '/api/'
        
        # Маршрутизация API
        if api_path == 'users' and context.method == 'GET':
            self.api_get_users(context)
        elif api_path.startswith('users/') and context.method == 'GET':
            self.api_get_user(context, api_path[6:])
        elif api_path == 'users' and context.method == 'POST':
            self.api_create_user(context)
        elif api_path.startswith('users/') and context.method == 'PUT':
            self.api_update_user(context, api_path[6:])
        elif api_path.startswith('users/') and context.method == 'DELETE':
            self.api_delete_user(context, api_path[6:])
        elif api_path.endswith('/subscribe') and context.method == 'POST':
            self.api_subscribe_user(context, api_path[:-10])
        elif api_path.endswith('/unsubscribe') and context.method == 'POST':
            self.api_unsubscribe_user(context, api_path[:-11])
        elif api_path == 'currencies' and context.method == 'GET':
            self.api_get_currencies(context)
        elif api_path.startswith('currencies/') and context.method == 'GET':
            self.api_get_currency(context, api_path[11:])
        elif api_path == 'exchange' and context.method == 'GET':
            self.api_calculate_exchange(context)
        else:
            self.handle_error(404, "API endpoint not found")
    
    def api_get_users(self, context: RequestContext):
        """API: Получить список пользователей."""
        users_data = [user.to_dict() for user in self.app_data['users']]
        response = {
            'success': True,
            'users': users_data,
            'count': len(users_data)
        }
        self.send_json_response(200, response)
    
    def api_get_user(self, context: RequestContext, user_id_str: str):
        """API: Получить пользователя по ID."""
        try:
            user_id = int(user_id_str)
            user = next((u for u in self.app_data['users'] if u.id == user_id), None)
            
            if user:
                response = {
                    'success': True,
                    'user': user.to_dict(include_subscriptions=True)
                }
                self.send_json_response(200, response)
            else:
                self.send_json_response(404, {'success': False, 'message': 'User not found'})
                
        except ValueError:
            self.send_json_response(400, {'success': False, 'message': 'Invalid user ID'})
    
    def api_create_user(self, context: RequestContext):
        """API: Создать нового пользователя."""
        data = context.get_json_body()
        
        if not data or 'name' not in data:
            self.send_json_response(400, {'success': False, 'message': 'Name is required'})
            return
        
        try:
            # Генерируем новый ID
            max_id = max((u.id for u in self.app_data['users']), default=0)
            new_id = max_id + 1
            
            # Создаем пользователя
            new_user = User(new_id, data['name'])
            self.app_data['users'].append(new_user)
            
            response = {
                'success': True,
                'message': 'User created successfully',
                'user': new_user.to_dict()
            }
            self.send_json_response(201, response)
            
        except Exception as e:
            self.send_json_response(500, {'success': False, 'message': str(e)})
    
    def api_update_user(self, context: RequestContext, user_id_str: str):
        """API: Обновить пользователя."""
        try:
            user_id = int(user_id_str)
            user = next((u for u in self.app_data['users'] if u.id == user_id), None)
            
            if not user:
                self.send_json_response(404, {'success': False, 'message': 'User not found'})
                return
            
            data = context.get_json_body()
            if not data or 'name' not in data:
                self.send_json_response(400, {'success': False, 'message': 'Name is required'})
                return
            
            # Обновляем пользователя
            user.name = data['name']
            
            response = {
                'success': True,
                'message': 'User updated successfully',
                'user': user.to_dict()
            }
            self.send_json_response(200, response)
            
        except ValueError:
            self.send_json_response(400, {'success': False, 'message': 'Invalid user ID'})
        except Exception as e:
            self.send_json_response(500, {'success': False, 'message': str(e)})
    
    def api_delete_user(self, context: RequestContext, user_id_str: str):
        """API: Удалить пользователя."""
        try:
            user_id = int(user_id_str)
            
            # Находим и удаляем пользователя
            initial_count = len(self.app_data['users'])
            self.app_data['users'] = [u for u in self.app_data['users'] if u.id != user_id]
            
            if len(self.app_data['users']) < initial_count:
                # Также удаляем все подписки этого пользователя
                self.app_data['subscriptions'] = [
                    sub for sub in self.app_data['subscriptions'] 
                    if sub.user_id != user_id
                ]
                
                response = {
                    'success': True,
                    'message': 'User deleted successfully'
                }
                self.send_json_response(200, response)
            else:
                self.send_json_response(404, {'success': False, 'message': 'User not found'})
                
        except ValueError:
            self.send_json_response(400, {'success': False, 'message': 'Invalid user ID'})
        except Exception as e:
            self.send_json_response(500, {'success': False, 'message': str(e)})
    
    def api_subscribe_user(self, context: RequestContext, user_id_str: str):
        """API: Подписать пользователя на валюту."""
        try:
            user_id = int(user_id_str)
            user = next((u for u in self.app_data['users'] if u.id == user_id), None)
            
            if not user:
                self.send_json_response(404, {'success': False, 'message': 'User not found'})
                return
            
            data = context.get_json_body()
            if not data or 'currency_id' not in data:
                self.send_json_response(400, {'success': False, 'message': 'Currency ID is required'})
                return
            
            currency_id = data['currency_id']
            
            # Проверяем существование валюты
            currency = next((c for c in self.app_data['currencies'] if c.id == currency_id), None)
            if not currency:
                self.send_json_response(404, {'success': False, 'message': 'Currency not found'})
                return
            
            # Добавляем подписку
            try:
                subscription = user.subscribe_to_currency(currency_id)
                self.app_data['subscriptions'].append(subscription)
                
                response = {
                    'success': True,
                    'message': 'Subscription added successfully',
                    'subscription': subscription.to_dict()
                }
                self.send_json_response(201, response)
                
            except ValueError as e:
                self.send_json_response(400, {'success': False, 'message': str(e)})
                
        except ValueError:
            self.send_json_response(400, {'success': False, 'message': 'Invalid user ID'})
        except Exception as e:
            self.send_json_response(500, {'success': False, 'message': str(e)})
    
    def api_unsubscribe_user(self, context: RequestContext, user_id_str: str):
        """API: Отписать пользователя от валюты."""
        try:
            user_id = int(user_id_str)
            user = next((u for u in self.app_data['users'] if u.id == user_id), None)
            
            if not user:
                self.send_json_response(404, {'success': False, 'message': 'User not found'})
                return
            
            data = context.get_json_body()
            if not data or 'currency_id' not in data:
                self.send_json_response(400, {'success': False, 'message': 'Currency ID is required'})
                return
            
            currency_id = data['currency_id']
            
            # Удаляем подписку
            if user.unsubscribe_from_currency(currency_id):
                # Также удаляем из общего списка подписок
                self.app_data['subscriptions'] = [
                    sub for sub in self.app_data['subscriptions'] 
                    if not (sub.user_id == user_id and sub.currency_id == currency_id)
                ]
                
                response = {
                    'success': True,
                    'message': 'Subscription removed successfully'
                }
                self.send_json_response(200, response)
            else:
                self.send_json_response(404, {'success': False, 'message': 'Subscription not found'})
                
        except ValueError:
            self.send_json_response(400, {'success': False, 'message': 'Invalid user ID'})
        except Exception as e:
            self.send_json_response(500, {'success': False, 'message': str(e)})
    
    def api_get_currencies(self, context: RequestContext):
        """API: Получить список валют."""
        currencies_data = [currency.to_dict() for currency in self.app_data['currencies']]
        response = {
            'success': True,
            'currencies': currencies_data,
            'count': len(currencies_data),
            'last_update': self.app_data['last_currency_update'].isoformat() if self.app_data['last_currency_update'] else None
        }
        self.send_json_response(200, response)
    
    def api_get_currency(self, context: RequestContext, currency_id: str):
        """API: Получить валюту по ID."""
        currency = next((c for c in self.app_data['currencies'] if c.id == currency_id), None)
        
        if currency:
            response = {
                'success': True,
                'currency': currency.to_dict()
            }
            self.send_json_response(200, response)
        else:
            # Пробуем получить из API
            try:
                currency_details = get_currency_details(currency_id, config.CURRENCY_API_URL)
                if currency_details:
                    response = {
                        'success': True,
                        'currency': currency_details
                    }
                    self.send_json_response(200, response)
                else:
                    self.send_json_response(404, {'success': False, 'message': 'Currency not found'})
            except Exception as e:
                self.send_json_response(500, {'success': False, 'message': str(e)})
    
    def api_calculate_exchange(self, context: RequestContext):
        """API: Рассчитать обмен валют."""
        try:
            amount = float(context.get_first_param('amount', 1))
            from_currency = context.get_first_param('from', 'USD')
            to_currency = context.get_first_param('to', 'RUB')
            
            result = calculate_exchange(amount, from_currency, to_currency, config.CURRENCY_API_URL)
            
            if result is not None:
                response = {
                    'success': True,
                    'amount': amount,
                    'from': from_currency,
                    'to': to_currency,
                    'result': result,
                    'rate': result / amount if amount > 0 else 0
                }
                self.send_json_response(200, response)
            else:
                self.send_json_response(400, {'success': False, 'message': 'Could not calculate exchange'})
                
        except ValueError:
            self.send_json_response(400, {'success': False, 'message': 'Invalid parameters'})
        except Exception as e:
            self.send_json_response(500, {'success': False, 'message': str(e)})
    
    def handle_404(self, context: RequestContext):
        """Обработка 404 ошибки (страница не найдена)."""
        error_template = self.env.get_template('error.html') if os.path.exists('templates/error.html') else None
        
        if error_template:
            html_content = error_template.render(
                error_code=404,
                error_message="Страница не найдена",
                app_version=config.APP_VERSION,
                author_name=config.AUTHOR_NAME,
                author_group=config.AUTHOR_GROUP
            )
            self.send_response(404)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))
        else:
            error_message = "404 - Страница не найдена"
            self.send_error(404, error_message)
    
    def handle_error(self, status_code: int, message: str):
        """Обработка ошибок."""
        try:
            error_template = self.env.get_template('error.html') if os.path.exists('templates/error.html') else None
            
            if error_template:
                html_content = error_template.render(
                    error_code=status_code,
                    error_message=message,
                    app_version=config.APP_VERSION,
                    author_name=config.AUTHOR_NAME,
                    author_group=config.AUTHOR_GROUP
                )
                self.send_response(status_code)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(html_content.encode('utf-8'))
            else:
                self.send_error(status_code, message)
        except Exception as e:
            logger.error(f"Error rendering error page: {e}")
            self.send_error(status_code, message)
    
    def send_json_response(self, status_code: int, data: Dict[str, Any]):
        """Отправить JSON ответ."""
        json_data = json.dumps(data, ensure_ascii=False, indent=2)
        
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(json_data.encode('utf-8'))))
        self.end_headers()
        self.wfile.write(json_data.encode('utf-8'))
    
    def update_currencies_from_api(self):
        """Обновить курсы валют из API."""
        try:
            # Получаем актуальные курсы
            currency_codes = [c.char_code for c in self.app_data['currencies']]
            new_rates = get_currencies(currency_codes, config.CURRENCY_API_URL, config.CURRENCY_API_TIMEOUT)
            
            # Обновляем курсы в существующих объектах Currency
            for currency in self.app_data['currencies']:
                if currency.char_code in new_rates:
                    currency.value = new_rates[currency.char_code]
                    currency.last_updated = datetime.now()
            
            self.app_data['last_currency_update'] = datetime.now()
            logger.info("Курсы валют успешно обновлены")
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении курсов валют: {e}")
    
    def generate_chart_data(self, currencies: List[Currency]) -> Dict[str, Any]:
        """
        Генерировать данные для графика динамики курсов.
        
        Args:
            currencies: Список валют для отображения на графике
        
        Returns:
            Данные в формате Chart.js
        """
        import random
        from datetime import datetime, timedelta
        
        chart_data = {
            'labels': [],
            'datasets': []
        }
        
        if not currencies:
            return chart_data
        
        # Генерируем даты за последние 3 месяца (примерно 90 дней)
        today = datetime.now()
        dates = []
        for i in range(90, -1, -7):  # Раз в неделю
            date = today - timedelta(days=i)
            dates.append(date.strftime('%d.%m'))
        
        chart_data['labels'] = dates
        
        # Цвета для графиков
        colors = [
            {'border': '#FF6384', 'background': 'rgba(255, 99, 132, 0.1)'},
            {'border': '#36A2EB', 'background': 'rgba(54, 162, 235, 0.1)'},
            {'border': '#FFCE56', 'background': 'rgba(255, 206, 86, 0.1)'},
            {'border': '#4BC0C0', 'background': 'rgba(75, 192, 192, 0.1)'},
            {'border': '#9966FF', 'background': 'rgba(153, 102, 255, 0.1)'},
        ]
        
        # Генерируем данные для каждой валюты
        for idx, currency in enumerate(currencies):
            color = colors[idx % len(colors)]
            
            # Создаем базовый тренд с небольшими случайными колебаниями
            base_value = currency.value
            values = []
            
            for i in range(len(dates)):
                # Симулируем изменение курса
                trend = random.uniform(-0.1, 0.1) * base_value * (i / len(dates))
                noise = random.uniform(-0.02, 0.02) * base_value
                value = base_value + trend + noise
                values.append(round(value, 4))
            
            dataset = {
                'label': f'{currency.char_code} - {currency.name}',
                'data': values,
                'borderColor': color['border'],
                'backgroundColor': color['background'],
                'borderWidth': 2,
                'fill': True,
                'tension': 0.4,
                'pointRadius': 2,
                'pointHoverRadius': 5
            }
            
            chart_data['datasets'].append(dataset)
        
        return chart_data
    
    def format_datetime(self, dt: Optional[datetime]) -> str:
        """Форматировать datetime в строку."""
        if dt is None:
            return "Неизвестно"
        
        # Форматируем дату и время по-русски
        months = {
            1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля',
            5: 'мая', 6: 'июня', 7: 'июля', 8: 'августа',
            9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'
        }
        
        day = dt.day
        month = months.get(dt.month, '')
        year = dt.year
        hour = dt.hour
        minute = dt.minute
        
        return f"{day} {month} {year} года, {hour:02d}:{minute:02d}"
    
    def count_lines_of_code(self) -> int:
        """Подсчитать количество строк кода в проекте."""
        total_lines = 0
        
        # Расширения файлов Python
        python_extensions = ('.py',)
        
        # Директории для подсчета
        directories = ['models', 'templates', 'static', 'utils', '.']
        
        for directory in directories:
            if not os.path.exists(directory):
                continue
            
            for root, dirs, files in os.walk(directory):
                # Пропускаем служебные директории
                dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
                
                for file in files:
                    filepath = os.path.join(root, file)
                    
                    # Считаем только Python файлы и HTML/JS/CSS
                    if file.endswith(python_extensions) or file.endswith(('.html', '.js', '.css')):
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                lines = f.readlines()
                                total_lines += len(lines)
                        except:
                            pass
        
        return total_lines
    
    def count_project_files(self) -> int:
        """Подсчитать количество файлов в проекте."""
        total_files = 0
        
        # Директории для подсчета
        directories = ['models', 'templates', 'static', 'utils', '.']
        
        for directory in directories:
            if not os.path.exists(directory):
                continue
            
            for root, dirs, files in os.walk(directory):
                # Пропускаем служебные директории
                dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
                
                # Считаем только определенные типы файлов
                for file in files:
                    if file.endswith(('.py', '.html', '.js', '.css', '.txt', '.md')):
                        total_files += 1
        
        return total_files


def run_server():
    """Запустить сервер."""
    server_address = (config.SERVER_HOST, config.SERVER_PORT)
    
    try:
        httpd = HTTPServer(server_address, CurrencyTrackerServer)
        
        print("=" * 60)
        print(f"Сервер Currency Tracker запущен!")
        print(f"Адрес: http://{config.SERVER_HOST}:{config.SERVER_PORT}")
        print(f"Версия приложения: {config.APP_VERSION}")
        print(f"Автор: {config.AUTHOR_NAME} ({config.AUTHOR_GROUP})")
        print("=" * 60)
        print("Доступные маршруты:")
        print("  /              - Главная страница")
        print("  /users         - Список пользователей")
        print("  /user?id=...   - Страница пользователя")
        print("  /currencies    - Курсы валют")
        print("  /author        - Информация об авторе")
        print("  /api/*         - API endpoints")
        print("=" * 60)
        print("Нажмите Ctrl+C для остановки сервера")
        print("=" * 60)
        
        # Запускаем сервер
        httpd.serve_forever()
        
    except KeyboardInterrupt:
        print("\nСервер остановлен пользователем")
    except Exception as e:
        print(f"Ошибка при запуске сервера: {e}")
        sys.exit(1)


if __name__ == '__main__':
    run_server()