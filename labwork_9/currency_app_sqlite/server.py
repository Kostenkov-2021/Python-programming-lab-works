"""
Основное приложение с HTTP сервером и роутингом.
"""

import sqlite3
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, unquote
from typing import Dict, Any
import json

from controllers.databasecontroller import DatabaseController, CurrencyRatesCRUD
from controllers.currencycontroller import CurrencyController
from controllers.pages import PagesController


class CurrencyApp(BaseHTTPRequestHandler):
    """HTTP сервер приложения Currency Tracker."""
    
    # Инициализация контроллеров (будет выполнена при создании сервера)
    db_controller = None
    currency_crud = None
    currency_controller = None
    pages_controller = None
    
    @classmethod
    def init_controllers(cls):
        """Инициализировать контроллеры приложения."""
        # Создаем контроллер базы данных (в памяти)
        cls.db_controller = DatabaseController(":memory:")
        
        # Создаем CRUD контроллер для валют
        cls.currency_crud = CurrencyRatesCRUD(cls.db_controller)
        
        # Создаем контроллер бизнес-логики для валют
        cls.currency_controller = CurrencyController(cls.currency_crud)
        
        # Создаем контроллер для рендеринга страниц
        cls.pages_controller = PagesController("templates")
    
    def do_GET(self):
        """Обработать GET запрос."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)
        
        # Маршрутизация
        if path == '/':
            self.handle_index()
        elif path == '/author':
            self.handle_author()
        elif path == '/users':
            self.handle_users()
        elif path == '/user':
            self.handle_user(query_params)
        elif path == '/currencies':
            self.handle_currencies()
        elif path == '/currency/delete':
            self.handle_currency_delete(query_params)
        elif path == '/currency/update':
            self.handle_currency_update(query_params)
        elif path == '/currency/show':
            self.handle_currency_show()
        elif path.startswith('/static/'):
            self.handle_static(path)
        else:
            self.handle_404()
    
    def handle_index(self):
        """Обработать главную страницу."""
        html_content = self.pages_controller.render_index(self.db_controller)
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def handle_author(self):
        """Обработать страницу об авторе."""
        html_content = self.pages_controller.render_author(self.db_controller)
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def handle_users(self):
        """Обработать страницу пользователей."""
        html_content = self.pages_controller.render_users(self.db_controller)
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def handle_user(self, query_params: Dict[str, list]):
        """Обработать страницу конкретного пользователя."""
        user_id = query_params.get('id', [None])[0]
        
        if user_id is None:
            self.send_error(400, "Не указан ID пользователя")
            return
        
        try:
            user_id = int(user_id)
            html_content = self.pages_controller.render_user(self.db_controller, user_id)
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))
        except ValueError:
            self.send_error(400, "Неверный формат ID пользователя")
    
    def handle_currencies(self):
        """Обработать страницу валют."""
        html_content = self.pages_controller.render_currencies(
            self.db_controller, 
            self.currency_controller
        )
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def handle_currency_delete(self, query_params: Dict[str, list]):
        """Обработать удаление валюты."""
        currency_id = query_params.get('id', [None])[0]
        
        if currency_id is None:
            self.send_error(400, "Не указан ID валюты")
            return
        
        try:
            currency_id = int(currency_id)
            
            # Удаляем валюту
            success = self.currency_controller.delete_currency(currency_id)
            
            if success:
                # Перенаправляем на страницу валют
                self.send_response(302)
                self.send_header('Location', '/currencies')
                self.end_headers()
            else:
                self.send_error(404, "Валюта не найдена")
                
        except ValueError:
            self.send_error(400, "Неверный формат ID валюты")
    
    def handle_currency_update(self, query_params: Dict[str, list]):
        """Обработать обновление курса валюты."""
        # Извлекаем все параметры, которые могут быть кодами валют
        updates = {}
        for key, value in query_params.items():
            if len(key) == 3 and value:  # Коды валют обычно из 3 символов
                try:
                    new_value = float(value[0])
                    updates[key.upper()] = new_value
                except ValueError:
                    continue
        
        if not updates:
            self.send_error(400, "Не указаны курсы для обновления")
            return
        
        # Обновляем курсы
        success = True
        for char_code, value in updates.items():
            if not self.currency_controller.update_currency(char_code, value):
                success = False
        
        if success:
            # Перенаправляем на страницу валют
            self.send_response(302)
            self.send_header('Location', '/currencies')
            self.end_headers()
        else:
            self.send_error(400, "Ошибка обновления курсов")
    
    def handle_currency_show(self):
        """Показать информацию о валютах в консоли (для отладки)."""
        currencies = self.currency_controller.list_currencies()
        
        response = {
            'success': True,
            'count': len(currencies),
            'currencies': currencies
        }
        
        json_response = json.dumps(response, ensure_ascii=False, indent=2)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json_response.encode('utf-8'))
    
    def handle_static(self, path: str):
        """Обработать статические файлы."""
        try:
            # Убираем /static/ из пути
            file_path = unquote(path[7:])  # 7 = len('/static/')
            
            # Защита от directory traversal
            if '..' in file_path or file_path.startswith('/'):
                self.send_error(403, "Доступ запрещен")
                return
            
            # Определяем MIME тип
            mime_types = {
                '.css': 'text/css',
                '.js': 'application/javascript',
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.gif': 'image/gif',
                '.svg': 'image/svg+xml',
                '.ico': 'image/x-icon'
            }
            
            # Полный путь к файлу
            full_path = f"static/{file_path}"
            
            # Читаем файл
            with open(full_path, 'rb') as f:
                content = f.read()
            
            # Определяем расширение
            import os
            _, ext = os.path.splitext(file_path)
            content_type = mime_types.get(ext.lower(), 'application/octet-stream')
            
            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            
        except FileNotFoundError:
            self.send_error(404, "Файл не найден")
        except Exception as e:
            self.send_error(500, f"Ошибка сервера: {str(e)}")
    
    def handle_404(self):
        """Обработать 404 ошибку."""
        html_content = self.pages_controller.render_error(
            404, "Страница не найдена"
        )
        self.send_response(404)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Логировать сообщения сервера."""
        # Можно настроить логирование по необходимости
        pass


def run_server(host: str = "localhost", port: int = 8080):
    """
    Запустить HTTP сервер.
    
    Args:
        host: Хост сервера
        port: Порт сервера
    """
    # Инициализируем контроллеры
    CurrencyApp.init_controllers()
    
    server_address = (host, port)
    httpd = HTTPServer(server_address, CurrencyApp)
    
    print("=" * 60)
    print(f"Сервер Currency Tracker запущен!")
    print(f"Адрес: http://{host}:{port}")
    print("=" * 60)
    print("Доступные маршруты:")
    print("  /                  - Главная страница")
    print("  /author            - Информация об авторе")
    print("  /users             - Список пользователей")
    print("  /user?id=...       - Страница пользователя")
    print("  /currencies        - Список валют")
    print("  /currency/delete?id=... - Удаление валюты")
    print("  /currency/update?USD=... - Обновление курса")
    print("  /currency/show     - JSON с валютами (для отладки)")
    print("=" * 60)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nСервер остановлен")
        
        # Закрываем соединение с БД
        if CurrencyApp.db_controller:
            CurrencyApp.db_controller.close()


if __name__ == '__main__':
    run_server()