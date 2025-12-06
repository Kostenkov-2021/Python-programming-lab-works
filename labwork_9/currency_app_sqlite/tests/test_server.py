"""
Тесты для серверной логики приложения.
"""

import unittest
import sys
import os
import json
from unittest.mock import Mock, patch, MagicMock

# Добавляем путь для импорта модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import CurrencyTrackerServer, RequestContext
from models import Author, App, User, Currency
from config import current_config as config


class TestServer(unittest.TestCase):
    """Тесты для серверной логики."""
    
    def setUp(self):
        """Подготовка тестов."""
        # Создаем мок-объект сервера
        self.mock_request = Mock()
        self.mock_client_address = ('localhost', 8080)
        self.mock_server = Mock()
        
        # Инициализируем сервер
        self.server = CurrencyTrackerServer(
            self.mock_request,
            self.mock_client_address,
            self.mock_server
        )
    
    def test_request_context_creation(self):
        """Тест создания контекста запроса."""
        context = RequestContext(
            path='/users',
            query_params={'id': ['1']},
            method='GET',
            headers={'Content-Type': 'text/html'}
        )
        
        self.assertEqual(context.path, '/users')
        self.assertEqual(context.get_first_param('id'), '1')
        self.assertEqual(context.get_first_param('name'), None)
        self.assertEqual(context.get_first_param('name', 'default'), 'default')
    
    def test_request_context_json_body(self):
        """Тест парсинга JSON тела запроса."""
        # С корректным JSON
        context = RequestContext(
            path='/api/users',
            query_params={},
            method='POST',
            headers={'Content-Type': 'application/json'},
            body=b'{"name": "John", "age": 30}'
        )
        
        json_data = context.get_json_body()
        self.assertEqual(json_data['name'], 'John')
        self.assertEqual(json_data['age'], 30)
        
        # С некорректным JSON
        context.body = b'not a json'
        json_data = context.get_json_body()
        self.assertIsNone(json_data)
        
        # Без тела
        context.body = None
        json_data = context.get_json_body()
        self.assertIsNone(json_data)
    
    @patch('server.CurrencyTrackerServer.send_response')
    @patch('server.CurrencyTrackerServer.send_header')
    @patch('server.CurrencyTrackerServer.end_headers')
    @patch('server.CurrencyTrackerServer.wfile')
    def test_send_json_response(self, mock_wfile, mock_end_headers, mock_send_header, mock_send_response):
        """Тест отправки JSON ответа."""
        # Настраиваем моки
        mock_wfile.write = Mock()
        
        # Вызываем метод
        test_data = {'success': True, 'message': 'Test'}
        self.server.send_json_response(200, test_data)
        
        # Проверяем вызовы
        mock_send_response.assert_called_once_with(200)
        mock_send_header.assert_any_call('Content-type', 'application/json; charset=utf-8')
        
        # Проверяем отправленные данные
        call_args = mock_wfile.write.call_args[0][0]
        written_data = json.loads(call_args.decode('utf-8'))
        self.assertEqual(written_data, test_data)
    
    def test_generate_chart_data(self):
        """Тест генерации данных для графика."""
        # Создаем тестовые валюты
        currencies = [
            Currency("R01235", "840", "USD", "Доллар США", 93.25, 1),
            Currency("R01239", "978", "EUR", "Евро", 101.70, 1)
        ]
        
        # Генерируем данные
        chart_data = self.server.generate_chart_data(currencies)
        
        # Проверяем структуру
        self.assertIn('labels', chart_data)
        self.assertIn('datasets', chart_data)
        self.assertIsInstance(chart_data['labels'], list)
        self.assertIsInstance(chart_data['datasets'], list)
        
        # Проверяем количество наборов данных
        self.assertEqual(len(chart_data['datasets']), 2)
        
        # Проверяем структуру каждого набора
        for dataset in chart_data['datasets']:
            self.assertIn('label', dataset)
            self.assertIn('data', dataset)
            self.assertIn('borderColor', dataset)
            self.assertIn('backgroundColor', dataset)
            self.assertIsInstance(dataset['data'], list)
            self.assertEqual(len(dataset['data']), len(chart_data['labels']))
    
    def test_generate_chart_data_empty(self):
        """Тест генерации данных для графика с пустым списком."""
        chart_data = self.server.generate_chart_data([])
        
        self.assertIn('labels', chart_data)
        self.assertIn('datasets', chart_data)
        self.assertEqual(len(chart_data['labels']), 0)
        self.assertEqual(len(chart_data['datasets']), 0)
    
    def test_format_datetime(self):
        """Тест форматирования даты и времени."""
        from datetime import datetime
        
        # Тест с корректной датой
        test_date = datetime(2024, 1, 15, 14, 30)
        formatted = self.server.format_datetime(test_date)
        
        self.assertIn("января", formatted)
        self.assertIn("2024", formatted)
        self.assertIn("14:30", formatted)
        
        # Тест с None
        formatted = self.server.format_datetime(None)
        self.assertEqual(formatted, "Неизвестно")
    
    @patch('os.path.exists')
    @patch('os.walk')
    def test_count_lines_of_code(self, mock_walk, mock_exists):
        """Тест подсчета строк кода."""
        # Настраиваем моки
        mock_exists.return_value = True
        mock_walk.return_value = [
            ('.', [], ['server.py', 'config.py']),
            ('models', [], ['user.py', 'currency.py'])
        ]
        
        # Мокаем чтение файлов
        with patch('builtins.open', unittest.mock.mock_open(read_data='line1\nline2\nline3\n')):
            lines_count = self.server.count_lines_of_code()
        
        # 2 файла в корне + 2 файла в models = 4 файла
        # Каждый файл имеет 3 строки
        self.assertEqual(lines_count, 12)
    
    @patch('os.path.exists')
    @patch('os.walk')
    def test_count_project_files(self, mock_walk, mock_exists):
        """Тест подсчета файлов проекта."""
        # Настраиваем моки
        mock_exists.return_value = True
        mock_walk.return_value = [
            ('.', [], ['server.py', 'README.md', 'requirements.txt']),
            ('models', [], ['user.py', '__init__.py']),
            ('templates', [], ['index.html', 'base.html'])
        ]
        
        files_count = self.server.count_project_files()
        
        # server.py, requirements.txt, user.py, __init__.py, index.html, base.html = 6 файлов
        # README.md не считается (только .py, .html, .js, .css, .txt, .md)
        self.assertEqual(files_count, 6)


class TestAppDataInitialization(unittest.TestCase):
    """Тесты инициализации данных приложения."""
    
    def test_app_data_structure(self):
        """Тест структуры данных приложения."""
        # Создаем сервер
        mock_request = Mock()
        mock_client_address = ('localhost', 8080)
        mock_server = Mock()
        
        server = CurrencyTrackerServer(
            mock_request,
            mock_client_address,
            mock_server
        )
        
        # Проверяем структуру app_data
        self.assertIn('app', server.app_data)
        self.assertIn('users', server.app_data)
        self.assertIn('currencies', server.app_data)
        self.assertIn('subscriptions', server.app_data)
        self.assertIn('last_currency_update', server.app_data)
        
        # Проверяем типы
        self.assertIsInstance(server.app_data['app'], App)
        self.assertIsInstance(server.app_data['users'], list)
        self.assertIsInstance(server.app_data['currencies'], list)
        self.assertIsInstance(server.app_data['subscriptions'], list)
        
        # Проверяем наличие начальных данных
        self.assertGreater(len(server.app_data['users']), 0)
        self.assertGreater(len(server.app_data['currencies']), 0)
        self.assertGreater(len(server.app_data['subscriptions']), 0)
    
    def test_app_initialization(self):
        """Тест инициализации приложения."""
        mock_request = Mock()
        mock_client_address = ('localhost', 8080)
        mock_server = Mock()
        
        server = CurrencyTrackerServer(
            mock_request,
            mock_client_address,
            mock_server
        )
        
        # Проверяем данные приложения
        app = server.app_data['app']
        self.assertEqual(app.name, config.APP_NAME)
        self.assertEqual(app.version, config.APP_VERSION)
        self.assertEqual(app.author.name, config.AUTHOR_NAME)
        self.assertEqual(app.author.group, config.AUTHOR_GROUP)
        
        # Проверяем, что пользователи созданы
        user_names = [user.name for user in server.app_data['users']]
        for initial_user in config.INITIAL_USERS:
            self.assertIn(initial_user['name'], user_names)
        
        # Проверяем, что валюты созданы
        currency_codes = [currency.char_code for currency in server.app_data['currencies']]
        for initial_currency in config.INITIAL_CURRENCIES:
            self.assertIn(initial_currency['char_code'], currency_codes)


class TestAPIMethods(unittest.TestCase):
    """Тесты API методов."""
    
    def setUp(self):
        """Подготовка тестов."""
        mock_request = Mock()
        mock_client_address = ('localhost', 8080)
        mock_server = Mock()
        
        self.server = CurrencyTrackerServer(
            mock_request,
            mock_client_address,
            mock_server
        )
        
        # Мокаем методы отправки ответа
        self.server.send_json_response = Mock()
    
    def test_api_get_users(self):
        """Тест API получения списка пользователей."""
        # Создаем контекст запроса
        context = RequestContext(
            path='/api/users',
            query_params={},
            method='GET',
            headers={}
        )
        
        # Вызываем метод
        self.server.api_get_users(context)
        
        # Проверяем вызов send_json_response
        self.server.send_json_response.assert_called_once()
        
        # Получаем переданные данные
        call_args = self.server.send_json_response.call_args
        status_code = call_args[0][0]
        response_data = call_args[0][1]
        
        self.assertEqual(status_code, 200)
        self.assertTrue(response_data['success'])
        self.assertIn('users', response_data)
        self.assertIn('count', response_data)
        self.assertEqual(response_data['count'], len(response_data['users']))
    
    def test_api_get_user_valid(self):
        """Тест API получения пользователя по ID."""
        # Получаем первого пользователя
        user = self.server.app_data['users'][0]
        
        # Создаем контекст запроса
        context = RequestContext(
            path=f'/api/users/{user.id}',
            query_params={},
            method='GET',
            headers={}
        )
        
        # Вызываем метод
        self.server.api_get_user(context, str(user.id))
        
        # Проверяем вызов send_json_response
        self.server.send_json_response.assert_called_once()
        
        # Получаем переданные данные
        call_args = self.server.send_json_response.call_args
        status_code = call_args[0][0]
        response_data = call_args[0][1]
        
        self.assertEqual(status_code, 200)
        self.assertTrue(response_data['success'])
        self.assertIn('user', response_data)
        self.assertEqual(response_data['user']['id'], user.id)
        self.assertEqual(response_data['user']['name'], user.name)
    
    def test_api_get_user_invalid(self):
        """Тест API получения несуществующего пользователя."""
        # Создаем контекст запроса с несуществующим ID
        context = RequestContext(
            path='/api/users/999',
            query_params={},
            method='GET',
            headers={}
        )
        
        # Вызываем метод
        self.server.api_get_user(context, '999')
        
        # Проверяем вызов send_json_response
        self.server.send_json_response.assert_called_once()
        
        # Получаем переданные данные
        call_args = self.server.send_json_response.call_args
        status_code = call_args[0][0]
        response_data = call_args[0][1]
        
        self.assertEqual(status_code, 404)
        self.assertFalse(response_data['success'])
        self.assertIn('message', response_data)
    
    def test_api_create_user(self):
        """Тест API создания пользователя."""
        # Определяем количество пользователей до создания
        initial_count = len(self.server.app_data['users'])
        
        # Создаем контекст запроса
        context = RequestContext(
            path='/api/users',
            query_params={},
            method='POST',
            headers={'Content-Type': 'application/json'},
            body=b'{"name": "Новый пользователь"}'
        )
        
        # Вызываем метод
        self.server.api_create_user(context)
        
        # Проверяем вызов send_json_response
        self.server.send_json_response.assert_called_once()
        
        # Получаем переданные данные
        call_args = self.server.send_json_response.call_args
        status_code = call_args[0][0]
        response_data = call_args[0][1]
        
        self.assertEqual(status_code, 201)
        self.assertTrue(response_data['success'])
        self.assertIn('user', response_data)
        self.assertEqual(response_data['user']['name'], 'Новый пользователь')
        
        # Проверяем, что пользователь добавлен
        self.assertEqual(len(self.server.app_data['users']), initial_count + 1)
    
    def test_api_create_user_invalid(self):
        """Тест API создания пользователя с некорректными данными."""
        # Создаем контекст запроса без имени
        context = RequestContext(
            path='/api/users',
            query_params={},
            method='POST',
            headers={'Content-Type': 'application/json'},
            body=b'{}'
        )
        
        # Вызываем метод
        self.server.api_create_user(context)
        
        # Проверяем вызов send_json_response
        self.server.send_json_response.assert_called_once()
        
        # Получаем переданные данные
        call_args = self.server.send_json_response.call_args
        status_code = call_args[0][0]
        response_data = call_args[0][1]
        
        self.assertEqual(status_code, 400)
        self.assertFalse(response_data['success'])
        self.assertIn('message', response_data)


if __name__ == '__main__':
    unittest.main(verbosity=2)