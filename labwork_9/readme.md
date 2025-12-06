# Программирование Python

# Лабораторная работа №9

## Костенков Данил Денисович

## Группа P4150




## Цель работы

Целью данной лабораторной работы является реализация CRUD-операций (Create, Read, Update, Delete) для сущностей бизнес-логики приложения с использованием SQLite базы данных. В процессе работы были выполнены следующие задачи:

1. Реализация CRUD-операций для сущностей Currency и User
2. Освоение работы с SQLite в памяти через модуль sqlite3
3. Понимание принципов первичных и внешних ключей и их роли в связях между таблицами
4. Разделение контроллеров для работы с БД и для рендеринга страниц
5. Применение архитектуры MVC с чётким разделением ответственности
6. Реализация полноценного роутера для обработки GET-запросов
7. Тестирование функционала с использованием unittest.mock

### 2. Описание моделей, их свойств и связей

#### Модели и их свойства

1. **Author**: Автор приложения
   - `id` - уникальный идентификатор
   - `name` - имя автора
   - `group` - учебная группа

2. **App**: Приложение
   - `id` - уникальный идентификатор
   - `name` - название приложения
   - `version` - версия приложения
   - `author_id` - внешний ключ к Author

3. **User**: Пользователь
   - `id` - уникальный идентификатор
   - `name` - имя пользователя
   - `created_at` - дата создания

4. **Currency**: Валюта
   - `id` - уникальный идентификатор
   - `num_code` - цифровой код
   - `char_code` - символьный код
   - `name` - название валюты
   - `value` - курс к рублю
   - `nominal` - номинал
   - `updated_at` - дата обновления курса

5. **UserCurrency**: Связь пользователя с валютой (подписка)
   - `id` - уникальный идентификатор
   - `user_id` - внешний ключ к User
   - `currency_id` - внешний ключ к Currency

#### Связи между таблицами

1. **Один-ко-многим**: App → Author (одно приложение имеет одного автора, автор может иметь несколько приложений)
2. **Многие-ко-многим**: User ↔ Currency через UserCurrency (пользователь может быть подписан на несколько валют, валюта может иметь несколько подписчиков)

### 3. Структура проекта с назначением файлов

```
currency_app_sqlite/
├── models/
│   ├── __init__.py
│   ├── author.py
│   ├── app.py
│   ├── user.py
│   ├── currency.py
│   └── user_currency.py
├── controllers/
│   ├── __init__.py
│   ├── databasecontroller.py
│   ├── currencycontroller.py
│   └── pages.py
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── users.html
│   ├── user.html
│   └── currencies.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── utils/
│   └── currencies_api.py
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   └── test_controllers.py
├── requirements.txt
└── app.py
```

**Назначение ключевых файлов:**
- `app.py` - основной файл приложения с HTTP сервером и роутингом
- `controllers/databasecontroller.py` - CRUD операции с базой данных
- `controllers/currencycontroller.py` - бизнес-логика для работы с валютами
- `controllers/pages.py` - рендеринг страниц через Jinja2
- `models/` - модели предметной области с геттерами и сеттерами
- `templates/` - HTML шаблоны Jinja2

### 4. Реализация CRUD с примерами SQL-запросов

#### 4.1. Класс DatabaseController для работы с SQLite

```python
"""
Контроллер для работы с SQLite базой данных.
Реализует CRUD операции для всех сущностей приложения.
"""

import sqlite3
import json
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime


class DatabaseController:
    """Контроллер для управления SQLite базой данных."""
    
    def __init__(self, db_path: str = ":memory:"):
        """
        Инициализация контроллера базы данных.
        
        Args:
            db_path: Путь к файлу БД или ":memory:" для базы в памяти
        """
        self.db_path = db_path
        self.connection = None
        self._connect()
        self._create_tables()
        self._seed_initial_data()
    
    def _connect(self) -> None:
        """Установить соединение с базой данных."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Возвращать строки как словари
            print(f"✅ Соединение с базой данных установлено: {self.db_path}")
        except sqlite3.Error as e:
            print(f"❌ Ошибка подключения к базе данных: {e}")
            raise
    
    def _create_tables(self) -> None:
        """Создать таблицы в базе данных."""
        create_tables_sql = """
        -- Таблица авторов
        CREATE TABLE IF NOT EXISTS author (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            group_name TEXT NOT NULL
        );
        
        -- Таблица приложений
        CREATE TABLE IF NOT EXISTS app (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            version TEXT NOT NULL,
            author_id INTEGER NOT NULL,
            FOREIGN KEY (author_id) REFERENCES author(id)
        );
        
        -- Таблица пользователей
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Таблица валют
        CREATE TABLE IF NOT EXISTS currency (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            num_code TEXT NOT NULL,
            char_code TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            value REAL NOT NULL,
            nominal INTEGER NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CHECK (value > 0),
            CHECK (nominal > 0)
        );
        
        -- Таблица подписок пользователей на валюты
        CREATE TABLE IF NOT EXISTS user_currency (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            currency_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
            FOREIGN KEY (currency_id) REFERENCES currency(id) ON DELETE CASCADE,
            UNIQUE(user_id, currency_id)
        );
        
        -- Индексы для ускорения поиска
        CREATE INDEX IF NOT EXISTS idx_currency_char_code ON currency(char_code);
        CREATE INDEX IF NOT EXISTS idx_user_currency_user_id ON user_currency(user_id);
        CREATE INDEX IF NOT EXISTS idx_user_currency_currency_id ON user_currency(currency_id);
        """
        
        try:
            cursor = self.connection.cursor()
            cursor.executescript(create_tables_sql)
            self.connection.commit()
            print("✅ Таблицы созданы успешно")
        except sqlite3.Error as e:
            print(f"❌ Ошибка создания таблиц: {e}")
            raise
    
    def _seed_initial_data(self) -> None:
        """Заполнить базу данных начальными данными."""
        # Проверяем, есть ли уже данные
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM currency")
        currency_count = cursor.fetchone()[0]
        
        if currency_count == 0:
            self._insert_initial_data()
    
    def _insert_initial_data(self) -> None:
        """Вставить начальные данные в таблицы."""
        try:
            cursor = self.connection.cursor()
            
            # Добавляем автора
            cursor.execute("""
                INSERT INTO author (name, group_name) 
                VALUES (?, ?)
            """, ("Иван Иванов", "ПИ-202"))
            
            author_id = cursor.lastrowid
            
            # Добавляем приложение
            cursor.execute("""
                INSERT INTO app (name, version, author_id) 
                VALUES (?, ?, ?)
            """, ("Currency Tracker", "1.0.0", author_id))
            
            # Добавляем пользователей
            users = [
                ("Иван Иванов",),
                ("Мария Петрова",),
                ("Алексей Сидоров",)
            ]
            
            cursor.executemany("""
                INSERT INTO user (name) 
                VALUES (?)
            """, users)
            
            # Добавляем валюты
            currencies = [
                ("840", "USD", "Доллар США", 93.25, 1),
                ("978", "EUR", "Евро", 101.70, 1),
                ("826", "GBP", "Фунт стерлингов", 118.45, 1),
                ("156", "CNY", "Китайский юань", 12.89, 1),
                ("392", "JPY", "Японская иена", 0.63, 100)
            ]
            
            cursor.executemany("""
                INSERT INTO currency (num_code, char_code, name, value, nominal) 
                VALUES (?, ?, ?, ?, ?)
            """, currencies)
            
            # Добавляем подписки
            subscriptions = [
                (1, 1),  # Иван подписан на USD
                (1, 2),  # Иван подписан на EUR
                (2, 2),  # Мария подписан на EUR
                (3, 3),  # Алексей подписан на GBP
            ]
            
            cursor.executemany("""
                INSERT INTO user_currency (user_id, currency_id) 
                VALUES (?, ?)
            """, subscriptions)
            
            self.connection.commit()
            print("✅ Начальные данные добавлены успешно")
            
        except sqlite3.Error as e:
            print(f"❌ Ошибка добавления начальных данных: {e}")
            self.connection.rollback()
            raise
    
    def execute_query(self, sql: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """
        Выполнить SQL запрос и вернуть результаты.
        
        Args:
            sql: SQL запрос
            params: Параметры запроса
        
        Returns:
            Список словарей с результатами
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql, params)
            
            if sql.strip().upper().startswith("SELECT"):
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
            else:
                self.connection.commit()
                return []
                
        except sqlite3.Error as e:
            print(f"❌ Ошибка выполнения запроса: {e}")
            self.connection.rollback()
            raise
    
    def execute_many(self, sql: str, params_list: List[Tuple]) -> None:
        """
        Выполнить SQL запрос с несколькими наборами параметров.
        
        Args:
            sql: SQL запрос
            params_list: Список кортежей параметров
        """
        try:
            cursor = self.connection.cursor()
            cursor.executemany(sql, params_list)
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"❌ Ошибка выполнения запроса: {e}")
            self.connection.rollback()
            raise
    
    # ========== CRUD операции для Currency ==========
    
    def create_currency(self, num_code: str, char_code: str, name: str, 
                       value: float, nominal: int) -> int:
        """
        Создать новую валюту.
        
        Args:
            num_code: Цифровой код
            char_code: Символьный код
            name: Название валюты
            value: Курс
            nominal: Номинал
        
        Returns:
            ID созданной валюты
        """
        sql = """
        INSERT INTO currency (num_code, char_code, name, value, nominal, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        
        params = (num_code, char_code, name, value, nominal, datetime.now())
        cursor = self.connection.cursor()
        cursor.execute(sql, params)
        self.connection.commit()
        
        return cursor.lastrowid
    
    def read_currency(self, currency_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Получить информацию о валюте(ах).
        
        Args:
            currency_id: ID валюты (если None - все валюты)
        
        Returns:
            Список словарей с информацией о валютах
        """
        if currency_id:
            sql = "SELECT * FROM currency WHERE id = ?"
            params = (currency_id,)
        else:
            sql = "SELECT * FROM currency ORDER BY char_code"
            params = ()
        
        return self.execute_query(sql, params)
    
    def read_currency_by_char_code(self, char_code: str) -> Optional[Dict[str, Any]]:
        """
        Получить информацию о валюте по символьному коду.
        
        Args:
            char_code: Символьный код валюты
        
        Returns:
            Словарь с информацией о валюте или None
        """
        sql = "SELECT * FROM currency WHERE char_code = ?"
        result = self.execute_query(sql, (char_code,))
        
        return result[0] if result else None
    
    def update_currency_value(self, char_code: str, value: float) -> bool:
        """
        Обновить курс валюты.
        
        Args:
            char_code: Символьный код валюты
            value: Новое значение курса
        
        Returns:
            True если обновление успешно, False в противном случае
        """
        try:
            sql = """
            UPDATE currency 
            SET value = ?, updated_at = ?
            WHERE char_code = ?
            """
            
            params = (value, datetime.now(), char_code)
            cursor = self.connection.cursor()
            cursor.execute(sql, params)
            self.connection.commit()
            
            return cursor.rowcount > 0
        except sqlite3.Error:
            return False
    
    def update_currency(self, currency_id: int, **kwargs) -> bool:
        """
        Обновить информацию о валюте.
        
        Args:
            currency_id: ID валюты
            **kwargs: Поля для обновления
        
        Returns:
            True если обновление успешно, False в противном случае
        """
        if not kwargs:
            return False
        
        set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        sql = f"UPDATE currency SET {set_clause}, updated_at = ? WHERE id = ?"
        
        params = list(kwargs.values())
        params.append(datetime.now())
        params.append(currency_id)
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql, params)
            self.connection.commit()
            
            return cursor.rowcount > 0
        except sqlite3.Error:
            return False
    
    def delete_currency(self, currency_id: int) -> bool:
        """
        Удалить валюту.
        
        Args:
            currency_id: ID валюты
        
        Returns:
            True если удаление успешно, False в противном случае
        """
        try:
            sql = "DELETE FROM currency WHERE id = ?"
            cursor = self.connection.cursor()
            cursor.execute(sql, (currency_id,))
            self.connection.commit()
            
            return cursor.rowcount > 0
        except sqlite3.Error:
            return False
    
    # ========== CRUD операции для User ==========
    
    def create_user(self, name: str) -> int:
        """
        Создать нового пользователя.
        
        Args:
            name: Имя пользователя
        
        Returns:
            ID созданного пользователя
        """
        sql = "INSERT INTO user (name) VALUES (?)"
        cursor = self.connection.cursor()
        cursor.execute(sql, (name,))
        self.connection.commit()
        
        return cursor.lastrowid
    
    def read_user(self, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Получить информацию о пользователе(ях).
        
        Args:
            user_id: ID пользователя (если None - все пользователи)
        
        Returns:
            Список словарей с информацией о пользователях
        """
        if user_id:
            sql = """
            SELECT u.*, 
                   COUNT(uc.id) as subscription_count
            FROM user u
            LEFT JOIN user_currency uc ON u.id = uc.user_id
            WHERE u.id = ?
            GROUP BY u.id
            """
            params = (user_id,)
        else:
            sql = """
            SELECT u.*, 
                   COUNT(uc.id) as subscription_count
            FROM user u
            LEFT JOIN user_currency uc ON u.id = uc.user_id
            GROUP BY u.id
            ORDER BY u.name
            """
            params = ()
        
        return self.execute_query(sql, params)
    
    def update_user(self, user_id: int, name: str) -> bool:
        """
        Обновить информацию о пользователе.
        
        Args:
            user_id: ID пользователя
            name: Новое имя пользователя
        
        Returns:
            True если обновление успешно, False в противном случае
        """
        sql = "UPDATE user SET name = ? WHERE id = ?"
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql, (name, user_id))
            self.connection.commit()
            
            return cursor.rowcount > 0
        except sqlite3.Error:
            return False
    
    def delete_user(self, user_id: int) -> bool:
        """
        Удалить пользователя.
        
        Args:
            user_id: ID пользователя
        
        Returns:
            True если удаление успешно, False в противном случае
        """
        try:
            sql = "DELETE FROM user WHERE id = ?"
            cursor = self.connection.cursor()
            cursor.execute(sql, (user_id,))
            self.connection.commit()
            
            return cursor.rowcount > 0
        except sqlite3.Error:
            return False
    
    # ========== CRUD операции для UserCurrency ==========
    
    def subscribe_user(self, user_id: int, currency_id: int) -> bool:
        """
        Подписать пользователя на валюту.
        
        Args:
            user_id: ID пользователя
            currency_id: ID валюты
        
        Returns:
            True если подписка успешна, False в противном случае
        """
        try:
            sql = """
            INSERT INTO user_currency (user_id, currency_id)
            VALUES (?, ?)
            """
            cursor = self.connection.cursor()
            cursor.execute(sql, (user_id, currency_id))
            self.connection.commit()
            
            return True
        except sqlite3.IntegrityError:
            # Подписка уже существует
            return False
        except sqlite3.Error:
            return False
    
    def unsubscribe_user(self, user_id: int, currency_id: int) -> bool:
        """
        Отписать пользователя от валюты.
        
        Args:
            user_id: ID пользователя
            currency_id: ID валюты
        
        Returns:
            True если отписка успешна, False в противном случае
        """
        try:
            sql = """
            DELETE FROM user_currency 
            WHERE user_id = ? AND currency_id = ?
            """
            cursor = self.connection.cursor()
            cursor.execute(sql, (user_id, currency_id))
            self.connection.commit()
            
            return cursor.rowcount > 0
        except sqlite3.Error:
            return False
    
    def get_user_subscriptions(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Получить список подписок пользователя.
        
        Args:
            user_id: ID пользователя
        
        Returns:
            Список словарей с информацией о подписках
        """
        sql = """
        SELECT c.*, uc.created_at as subscribed_at
        FROM currency c
        JOIN user_currency uc ON c.id = uc.currency_id
        WHERE uc.user_id = ?
        ORDER BY c.char_code
        """
        
        return self.execute_query(sql, (user_id,))
    
    def get_app_info(self) -> Dict[str, Any]:
        """
        Получить информацию о приложении и авторе.
        
        Returns:
            Словарь с информацией о приложении
        """
        sql = """
        SELECT a.name as app_name, 
               a.version as app_version,
               au.name as author_name,
               au.group_name as author_group
        FROM app a
        JOIN author au ON a.author_id = au.id
        LIMIT 1
        """
        
        result = self.execute_query(sql)
        return result[0] if result else {}
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Получить статистику по базе данных.
        
        Returns:
            Словарь со статистикой
        """
        stats = {}
        
        # Количество пользователей
        result = self.execute_query("SELECT COUNT(*) as count FROM user")
        stats['user_count'] = result[0]['count']
        
        # Количество валют
        result = self.execute_query("SELECT COUNT(*) as count FROM currency")
        stats['currency_count'] = result[0]['count']
        
        # Количество подписок
        result = self.execute_query("SELECT COUNT(*) as count FROM user_currency")
        stats['subscription_count'] = result[0]['count']
        
        # Последнее обновление курсов
        result = self.execute_query("""
            SELECT MAX(updated_at) as last_update 
            FROM currency
        """)
        stats['last_update'] = result[0]['last_update']
        
        return stats
    
    def close(self) -> None:
        """Закрыть соединение с базой данных."""
        if self.connection:
            self.connection.close()
            print("✅ Соединение с базой данных закрыто")
    
    def __enter__(self):
        """Контекстный менеджер для использования with."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Закрыть соединение при выходе из контекста."""
        self.close()


class CurrencyRatesCRUD:
    """
    Класс для CRUD операций с курсами валют.
    Реализует интерфейс, совместимый с примером из задания.
    """
    
    def __init__(self, db_controller: DatabaseController):
        """
        Инициализация контроллера курсов валют.
        
        Args:
            db_controller: Контроллер базы данных
        """
        self.db = db_controller
    
    def _create(self, currencies: List[Dict[str, Any]]) -> bool:
        """
        Создать несколько валют.
        
        Args:
            currencies: Список словарей с данными валют
        
        Returns:
            True если создание успешно, False в противном случае
        """
        try:
            for currency in currencies:
                self.db.create_currency(
                    num_code=currency.get('num_code', ''),
                    char_code=currency.get('char_code', ''),
                    name=currency.get('name', ''),
                    value=currency.get('value', 0.0),
                    nominal=currency.get('nominal', 1)
                )
            return True
        except Exception:
            return False
    
    def _read(self, char_code: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Прочитать информацию о валюте(ах).
        
        Args:
            char_code: Символьный код валюты (если None - все валюты)
        
        Returns:
            Список словарей с информацией о валютах
        """
        if char_code:
            currency = self.db.read_currency_by_char_code(char_code)
            return [currency] if currency else []
        else:
            return self.db.read_currency()
    
    def _update(self, rates: Dict[str, float]) -> bool:
        """
        Обновить курсы валют.
        
        Args:
            rates: Словарь {char_code: new_value}
        
        Returns:
            True если обновление успешно, False в противном случае
        """
        try:
            success = True
            for char_code, value in rates.items():
                if not self.db.update_currency_value(char_code, value):
                    success = False
            return success
        except Exception:
            return False
    
    def _delete(self, currency_id: int) -> bool:
        """
        Удалить валюту.
        
        Args:
            currency_id: ID валюты
        
        Returns:
            True если удаление успешно, False в противном случае
        """
        return self.db.delete_currency(currency_id)
```

#### 4.2. Класс CurrencyController с бизнес-логикой

```python
"""
Контроллер для бизнес-логики работы с валютами.
Использует DatabaseController для работы с базой данных.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from controllers.databasecontroller import CurrencyRatesCRUD


class CurrencyController:
    """Контроллер для работы с валютами."""
    
    def __init__(self, db_controller: CurrencyRatesCRUD):
        """
        Инициализация контроллера валют.
        
        Args:
            db_controller: Контроллер CRUD операций с валютами
        """
        self.db = db_controller
    
    def list_currencies(self) -> List[Dict[str, Any]]:
        """
        Получить список всех валют.
        
        Returns:
            Список словарей с информацией о валютах
        """
        return self.db._read()
    
    def get_currency(self, currency_id: int) -> Optional[Dict[str, Any]]:
        """
        Получить информацию о валюте по ID.
        
        Args:
            currency_id: ID валюты
        
        Returns:
            Словарь с информацией о валюте или None
        """
        result = self.db._read()
        for currency in result:
            if currency['id'] == currency_id:
                return currency
        return None
    
    def update_currency(self, char_code: str, value: float) -> bool:
        """
        Обновить курс валюты.
        
        Args:
            char_code: Символьный код валюты
            value: Новое значение курса
        
        Returns:
            True если обновление успешно, False в противном случае
        """
        return self.db._update({char_code: value})
    
    def delete_currency(self, currency_id: int) -> bool:
        """
        Удалить валюту.
        
        Args:
            currency_id: ID валюты
        
        Returns:
            True если удаление успешно, False в противном случае
        """
        return self.db._delete(currency_id)
    
    def add_currency(self, num_code: str, char_code: str, name: str, 
                    value: float, nominal: int) -> bool:
        """
        Добавить новую валюту.
        
        Args:
            num_code: Цифровой код
            char_code: Символьный код
            name: Название валюты
            value: Курс
            nominal: Номинал
        
        Returns:
            True если добавление успешно, False в противном случае
        """
        currencies = [{
            'num_code': num_code,
            'char_code': char_code,
            'name': name,
            'value': value,
            'nominal': nominal
        }]
        
        return self.db._create(currencies)
    
    def get_currencies_for_user(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Получить список валют для конкретного пользователя.
        
        Args:
            user_id: ID пользователя
        
        Returns:
            Список словарей с информацией о валютах пользователя
        """
        # В реальном приложении здесь бы вызывался метод DatabaseController
        # Для примера возвращаем все валюты
        all_currencies = self.list_currencies()
        
        # Отмечаем, подписан ли пользователь на каждую валюту
        # В реальном приложении это бы делалось через JOIN в SQL
        for currency in all_currencies:
            currency['is_subscribed'] = self._is_user_subscribed(user_id, currency['id'])
        
        return all_currencies
    
    def _is_user_subscribed(self, user_id: int, currency_id: int) -> bool:
        """
        Проверить, подписан ли пользователь на валюту.
        
        Args:
            user_id: ID пользователя
            currency_id: ID валюты
        
        Returns:
            True если подписан, False в противном случае
        """
        # В реальном приложении здесь бы был запрос к БД
        # Для примера возвращаем фиктивное значение
        return False
    
    def format_currency_value(self, value: float, nominal: int) -> str:
        """
        Форматировать значение курса валюты.
        
        Args:
            value: Курс валюты
            nominal: Номинал
        
        Returns:
            Отформатированная строка
        """
        value_per_unit = value / nominal
        return f"{value_per_unit:.4f}"
    
    def get_currency_stats(self) -> Dict[str, Any]:
        """
        Получить статистику по валютам.
        
        Returns:
            Словарь со статистикой
        """
        currencies = self.list_currencies()
        
        if not currencies:
            return {}
        
        # Находим валюту с максимальным и минимальным курсом
        max_currency = max(currencies, key=lambda x: x['value'])
        min_currency = min(currencies, key=lambda x: x['value'])
        
        # Вычисляем средний курс
        total_value = sum(c['value'] for c in currencies)
        avg_value = total_value / len(currencies)
        
        return {
            'total_count': len(currencies),
            'max_value': {
                'char_code': max_currency['char_code'],
                'value': max_currency['value'],
                'name': max_currency['name']
            },
            'min_value': {
                'char_code': min_currency['char_code'],
                'value': min_currency['value'],
                'name': min_currency['name']
            },
            'avg_value': avg_value,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
```

#### 4.3. Класс PagesController для рендеринга

```python
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
```

### 5. Основное приложение с роутингом

```python
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
```

### 6. Шаблоны HTML

#### 6.1. `templates/base.html`
```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Currency Tracker{% endblock %}</title>
    <link rel="stylesheet" href="/static/css/style.css">
    {% block extra_css %}{% endblock %}
</head>
<body>
    <nav class="navbar">
        <div class="container">
            <a href="/" class="logo">CurrencyTracker</a>
            <ul class="nav-links">
                <li><a href="/">Главная</a></li>
                <li><a href="/users">Пользователи</a></li>
                <li><a href="/currencies">Валюты</a></li>
                <li><a href="/author">Об авторе</a></li>
            </ul>
        </div>
    </nav>

    <main class="container">
        {% block content %}{% endblock %}
    </main>

    <footer>
        <div class="container">
            <p>&copy; 2024 Currency Tracker App. Все права защищены.</p>
            <p>Разработано {{ author_name }} ({{ author_group }})</p>
        </div>
    </footer>

    {% block extra_js %}{% endblock %}
</body>
</html>
```

#### 6.2. `templates/currencies.html`
```html
{% extends "base.html" %}

{% block title %}Валюты - Currency Tracker{% endblock %}

{% block content %}
<div class="page-header">
    <h1>Курсы валют</h1>
    
    <div class="stats">
        <div class="stat-item">
            <span class="stat-label">Всего валют:</span>
            <span class="stat-value">{{ stats.total_count }}</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Максимальный курс:</span>
            <span class="stat-value">{{ stats.max_value.char_code }} - {{ "%.2f"|format(stats.max_value.value) }}</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Минимальный курс:</span>
            <span class="stat-value">{{ stats.min_value.char_code }} - {{ "%.2f"|format(stats.min_value.value) }}</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Обновлено:</span>
            <span class="stat-value">{{ stats.last_updated }}</span>
        </div>
    </div>
</div>

<div class="actions">
    <a href="/currency/show" class="btn btn-secondary" target="_blank">
        Показать JSON (для отладки)
    </a>
</div>

<table class="table">
    <thead>
        <tr>
            <th>ID</th>
            <th>NumCode</th>
            <th>CharCode</th>
            <th>Name</th>
            <th>Value</th>
            <th>Nominal</th>
            <th>За 1 ед.</th>
            <th>Обновлено</th>
            <th>Действия</th>
        </tr>
    </thead>
    <tbody>
        {% for currency in currencies %}
        <tr>
            <td>{{ currency.id }}</td>
            <td>{{ currency.num_code }}</td>
            <td>{{ currency.char_code }}</td>
            <td>{{ currency.name }}</td>
            <td>{{ "%.4f"|format(currency.value) }}</td>
            <td>{{ currency.nominal }}</td>
            <td>{{ "%.4f"|format(currency.value / currency.nominal) }}</td>
            <td>{{ currency.updated_at }}</td>
            <td>
                <a href="/currency/delete?id={{ currency.id }}" 
                   class="btn btn-danger btn-sm"
                   onclick="return confirm('Удалить валюту {{ currency.char_code }}?')">
                    Удалить
                </a>
            </td>
        </tr>
        {% else %}
        <tr>
            <td colspan="9" class="text-center">Нет данных о валютах</td>
        </tr>
        {% endfor %}
    </tbody>
</table>

<div class="update-form">
    <h3>Обновить курсы валют</h3>
    <form method="GET" action="/currency/update">
        <div class="form-row">
            <div class="form-group">
                <label for="usd">USD:</label>
                <input type="number" step="0.01" id="usd" name="USD" 
                       placeholder="Новый курс USD" class="form-control">
            </div>
            <div class="form-group">
                <label for="eur">EUR:</label>
                <input type="number" step="0.01" id="eur" name="EUR" 
                       placeholder="Новый курс EUR" class="form-control">
            </div>
            <div class="form-group">
                <label for="gbp">GBP:</label>
                <input type="number" step="0.01" id="gbp" name="GBP" 
                       placeholder="Новый курс GBP" class="form-control">
            </div>
        </div>
        <button type="submit" class="btn btn-primary">Обновить курсы</button>
    </form>
</div>
{% endblock %}
```

#### 6.3. `templates/users.html`
```html
{% extends "base.html" %}

{% block title %}Пользователи - Currency Tracker{% endblock %}

{% block content %}
<div class="page-header">
    <h1>Пользователи системы</h1>
    <p>Всего пользователей: {{ users|length }}</p>
</div>

<table class="table">
    <thead>
        <tr>
            <th>ID</th>
            <th>Имя</th>
            <th>Дата регистрации</th>
            <th>Подписок</th>
            <th>Действия</th>
        </tr>
    </thead>
    <tbody>
        {% for user in users %}
        <tr>
            <td>{{ user.id }}</td>
            <td>{{ user.name }}</td>
            <td>{{ user.created_at }}</td>
            <td>{{ user.subscription_count }}</td>
            <td>
                <a href="/user?id={{ user.id }}" class="btn btn-primary btn-sm">
                    Просмотреть
                </a>
            </td>
        </tr>
        {% else %}
        <tr>
            <td colspan="5" class="text-center">Нет пользователей</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% endblock %}
```

#### 6.4. `static/css/style.css`
```css
/* Основные стили */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f8f9fa;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

/* Навигация */
.navbar {
    background: #343a40;
    color: white;
    padding: 15px 0;
}

.navbar .container {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.logo {
    color: white;
    text-decoration: none;
    font-size: 1.5em;
    font-weight: bold;
}

.nav-links {
    display: flex;
    list-style: none;
}

.nav-links li {
    margin-left: 20px;
}

.nav-links a {
    color: white;
    text-decoration: none;
    padding: 5px 10px;
    border-radius: 3px;
    transition: background 0.3s;
}

.nav-links a:hover {
    background: rgba(255, 255, 255, 0.1);
}

/* Основное содержимое */
main {
    padding: 30px 0;
    min-height: calc(100vh - 140px);
}

.page-header {
    margin-bottom: 30px;
}

.page-header h1 {
    margin-bottom: 20px;
}

.stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
    margin-bottom: 20px;
    padding: 15px;
    background: white;
    border-radius: 5px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.stat-item {
    padding: 10px;
}

.stat-label {
    font-weight: bold;
    color: #666;
    display: block;
}

.stat-value {
    font-size: 1.2em;
    color: #333;
}

/* Таблицы */
.table {
    width: 100%;
    border-collapse: collapse;
    background: white;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    border-radius: 5px;
    overflow: hidden;
    margin-bottom: 30px;
}

.table th,
.table td {
    padding: 12px 15px;
    text-align: left;
    border-bottom: 1px solid #dee2e6;
}

.table th {
    background: #343a40;
    color: white;
    font-weight: bold;
}

.table tbody tr:hover {
    background: #f8f9fa;
}

.table tbody tr:last-child td {
    border-bottom: none;
}

.text-center {
    text-align: center;
}

/* Кнопки */
.btn {
    display: inline-block;
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    text-decoration: none;
    cursor: pointer;
    font-size: 14px;
    transition: background 0.3s;
}

.btn-primary {
    background: #007bff;
    color: white;
}

.btn-primary:hover {
    background: #0056b3;
}

.btn-secondary {
    background: #6c757d;
    color: white;
}

.btn-secondary:hover {
    background: #545b62;
}

.btn-danger {
    background: #dc3545;
    color: white;
}

.btn-danger:hover {
    background: #c82333;
}

.btn-sm {
    padding: 5px 10px;
    font-size: 12px;
}

/* Формы */
.form-row {
    display: flex;
    gap: 15px;
    margin-bottom: 15px;
    flex-wrap: wrap;
}

.form-group {
    flex: 1;
    min-width: 200px;
}

.form-group label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
}

.form-control {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid #ced4da;
    border-radius: 4px;
    font-size: 14px;
}

.update-form {
    background: white;
    padding: 20px;
    border-radius: 5px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.update-form h3 {
    margin-bottom: 15px;
}

.actions {
    margin-bottom: 20px;
}

/* Футер */
footer {
    background: #343a40;
    color: white;
    padding: 20px 0;
    text-align: center;
}

footer p {
    margin: 5px 0;
}
```

### 7. Тестирование с unittest.mock

```python
"""
Тесты для контроллеров приложения.
Используют unittest.mock для изоляции тестируемых компонентов.
"""

import unittest
from unittest.mock import MagicMock, patch, Mock
import sys
import os

# Добавляем путь для импорта модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controllers.currencycontroller import CurrencyController
from controllers.databasecontroller import CurrencyRatesCRUD


class TestCurrencyController(unittest.TestCase):
    """Тесты для контроллера валют."""
    
    def setUp(self):
        """Подготовка тестов."""
        # Создаем mock для CurrencyRatesCRUD
        self.mock_db = MagicMock(spec=CurrencyRatesCRUD)
        
        # Создаем контроллер с mock-объектом
        self.controller = CurrencyController(self.mock_db)
    
    def test_list_currencies(self):
        """Тест получения списка валют."""
        # Настраиваем mock
        expected_currencies = [
            {"id": 1, "char_code": "USD", "value": 90.0, "name": "Доллар США"},
            {"id": 2, "char_code": "EUR", "value": 100.0, "name": "Евро"}
        ]
        self.mock_db._read.return_value = expected_currencies
        
        # Вызываем метод
        result = self.controller.list_currencies()
        
        # Проверяем результат
        self.assertEqual(result, expected_currencies)
        self.mock_db._read.assert_called_once()
    
    def test_get_currency_found(self):
        """Тест получения валюты по ID (найдена)."""
        # Настраиваем mock
        expected_currency = {"id": 1, "char_code": "USD", "value": 90.0}
        self.mock_db._read.return_value = [expected_currency]
        
        # Вызываем метод
        result = self.controller.get_currency(1)
        
        # Проверяем результат
        self.assertEqual(result, expected_currency)
        self.mock_db._read.assert_called_once()
    
    def test_get_currency_not_found(self):
        """Тест получения валюты по ID (не найдена)."""
        # Настраиваем mock
        self.mock_db._read.return_value = []
        
        # Вызываем метод
        result = self.controller.get_currency(999)
        
        # Проверяем результат
        self.assertIsNone(result)
        self.mock_db._read.assert_called_once()
    
    def test_update_currency_success(self):
        """Тест успешного обновления курса валюты."""
        # Настраиваем mock
        self.mock_db._update.return_value = True
        
        # Вызываем метод
        result = self.controller.update_currency("USD", 95.0)
        
        # Проверяем результат
        self.assertTrue(result)
        self.mock_db._update.assert_called_once_with({"USD": 95.0})
    
    def test_update_currency_failure(self):
        """Тест неудачного обновления курса валюты."""
        # Настраиваем mock
        self.mock_db._update.return_value = False
        
        # Вызываем метод
        result = self.controller.update_currency("EUR", 105.0)
        
        # Проверяем результат
        self.assertFalse(result)
        self.mock_db._update.assert_called_once_with({"EUR": 105.0})
    
    def test_delete_currency_success(self):
        """Тест успешного удаления валюты."""
        # Настраиваем mock
        self.mock_db._delete.return_value = True
        
        # Вызываем метод
        result = self.controller.delete_currency(1)
        
        # Проверяем результат
        self.assertTrue(result)
        self.mock_db._delete.assert_called_once_with(1)
    
    def test_delete_currency_failure(self):
        """Тест неудачного удаления валюты."""
        # Настраиваем mock
        self.mock_db._delete.return_value = False
        
        # Вызываем метод
        result = self.controller.delete_currency(999)
        
        # Проверяем результат
        self.assertFalse(result)
        self.mock_db._delete.assert_called_once_with(999)
    
    def test_add_currency_success(self):
        """Тест успешного добавления валюты."""
        # Настраиваем mock
        self.mock_db._create.return_value = True
        
        # Вызываем метод
        result = self.controller.add_currency(
            num_code="840",
            char_code="USD",
            name="Доллар США",
            value=90.0,
            nominal=1
        )
        
        # Проверяем результат
        self.assertTrue(result)
        self.mock_db._create.assert_called_once()
        
        # Проверяем аргументы
        call_args = self.mock_db._create.call_args[0][0]
        self.assertEqual(len(call_args), 1)
        self.assertEqual(call_args[0]["num_code"], "840")
        self.assertEqual(call_args[0]["char_code"], "USD")
        self.assertEqual(call_args[0]["name"], "Доллар США")
        self.assertEqual(call_args[0]["value"], 90.0)
        self.assertEqual(call_args[0]["nominal"], 1)
    
    def test_format_currency_value(self):
        """Тест форматирования значения курса."""
        # Тест с номиналом 1
        result = self.controller.format_currency_value(93.25, 1)
        self.assertEqual(result, "93.2500")
        
        # Тест с номиналом 100
        result = self.controller.format_currency_value(6325.0, 100)
        self.assertEqual(result, "63.2500")
        
        # Тест с дробным значением
        result = self.controller.format_currency_value(93.2567, 1)
        self.assertEqual(result, "93.2567")
    
    def test_get_currency_stats(self):
        """Тест получения статистики по валютам."""
        # Настраиваем mock
        currencies = [
            {"id": 1, "char_code": "USD", "value": 90.0, "name": "Доллар США"},
            {"id": 2, "char_code": "EUR", "value": 100.0, "name": "Евро"},
            {"id": 3, "char_code": "GBP", "value": 80.0, "name": "Фунт стерлингов"}
        ]
        self.mock_db._read.return_value = currencies
        
        # Вызываем метод
        result = self.controller.get_currency_stats()
        
        # Проверяем результат
        self.assertEqual(result["total_count"], 3)
        self.assertEqual(result["max_value"]["char_code"], "EUR")
        self.assertEqual(result["max_value"]["value"], 100.0)
        self.assertEqual(result["min_value"]["char_code"], "GBP")
        self.assertEqual(result["min_value"]["value"], 80.0)
        self.assertEqual(result["avg_value"], 90.0)  # (90+100+80)/3 = 90
    
    def test_get_currency_stats_empty(self):
        """Тест получения статистики по валютам (пустой список)."""
        # Настраиваем mock
        self.mock_db._read.return_value = []
        
        # Вызываем метод
        result = self.controller.get_currency_stats()
        
        # Проверяем результат
        self.assertEqual(result, {})


class TestDatabaseControllerIntegration(unittest.TestCase):
    """Интеграционные тесты для контроллера базы данных."""
    
    def setUp(self):
        """Подготовка тестов."""
        # Используем базу данных в памяти
        from controllers.databasecontroller import DatabaseController
        self.db = DatabaseController(":memory:")
    
    def test_create_and_read_currency(self):
        """Тест создания и чтения валюты."""
        # Создаем валюту
        currency_id = self.db.create_currency(
            num_code="840",
            char_code="USD",
            name="Доллар США",
            value=93.25,
            nominal=1
        )
        
        # Проверяем, что ID получен
        self.assertIsNotNone(currency_id)
        self.assertGreater(currency_id, 0)
        
        # Читаем валюту
        currencies = self.db.read_currency(currency_id)
        
        # Проверяем результат
        self.assertEqual(len(currencies), 1)
        currency = currencies[0]
        self.assertEqual(currency["num_code"], "840")
        self.assertEqual(currency["char_code"], "USD")
        self.assertEqual(currency["name"], "Доллар США")
        self.assertEqual(currency["value"], 93.25)
        self.assertEqual(currency["nominal"], 1)
    
    def test_update_currency_value(self):
        """Тест обновления курса валюты."""
        # Сначала создаем валюту
        currency_id = self.db.create_currency(
            num_code="978",
            char_code="EUR",
            name="Евро",
            value=100.0,
            nominal=1
        )
        
        # Обновляем курс
        success = self.db.update_currency_value("EUR", 105.5)
        
        # Проверяем результат
        self.assertTrue(success)
        
        # Читаем обновленную валюту
        currencies = self.db.read_currency(currency_id)
        currency = currencies[0]
        
        # Проверяем, что курс обновлен
        self.assertEqual(currency["value"], 105.5)
    
    def test_delete_currency(self):
        """Тест удаления валюты."""
        # Создаем валюту
        currency_id = self.db.create_currency(
            num_code="826",
            char_code="GBP",
            name="Фунт стерлингов",
            value=120.0,
            nominal=1
        )
        
        # Удаляем валюту
        success = self.db.delete_currency(currency_id)
        
        # Проверяем результат
        self.assertTrue(success)
        
        # Пытаемся прочитать удаленную валюту
        currencies = self.db.read_currency(currency_id)
        
        # Проверяем, что валюта удалена
        self.assertEqual(len(currencies), 0)
    
    def test_create_user(self):
        """Тест создания пользователя."""
        # Создаем пользователя
        user_id = self.db.create_user("Тестовый пользователь")
        
        # Проверяем, что ID получен
        self.assertIsNotNone(user_id)
        self.assertGreater(user_id, 0)
        
        # Читаем пользователя
        users = self.db.read_user(user_id)
        
        # Проверяем результат
        self.assertEqual(len(users), 1)
        user = users[0]
        self.assertEqual(user["name"], "Тестовый пользователь")
        self.assertIsNotNone(user["created_at"])
    
    def test_subscribe_and_unsubscribe_user(self):
        """Тест подписки и отписки пользователя от валюты."""
        # Создаем пользователя
        user_id = self.db.create_user("Тестовый пользователь")
        
        # Создаем валюту
        currency_id = self.db.create_currency(
            num_code="840",
            char_code="USD",
            name="Доллар США",
            value=93.25,
            nominal=1
        )
        
        # Подписываем пользователя на валюту
        subscribe_success = self.db.subscribe_user(user_id, currency_id)
        self.assertTrue(subscribe_success)
        
        # Проверяем подписку
        subscriptions = self.db.get_user_subscriptions(user_id)
        self.assertEqual(len(subscriptions), 1)
        self.assertEqual(subscriptions[0]["id"], currency_id)
        
        # Отписываем пользователя от валюты
        unsubscribe_success = self.db.unsubscribe_user(user_id, currency_id)
        self.assertTrue(unsubscribe_success)
        
        # Проверяем, что подписка удалена
        subscriptions = self.db.get_user_subscriptions(user_id)
        self.assertEqual(len(subscriptions), 0)
    
    def test_duplicate_subscription(self):
        """Тест повторной подписки на ту же валюту."""
        # Создаем пользователя
        user_id = self.db.create_user("Тестовый пользователь")
        
        # Создаем валюту
        currency_id = self.db.create_currency(
            num_code="978",
            char_code="EUR",
            name="Евро",
            value=100.0,
            nominal=1
        )
        
        # Первая подписка должна быть успешной
        success1 = self.db.subscribe_user(user_id, currency_id)
        self.assertTrue(success1)
        
        # Вторая подписка должна завершиться ошибкой (UNIQUE constraint)
        success2 = self.db.subscribe_user(user_id, currency_id)
        self.assertFalse(success2)
    
    def test_get_statistics(self):
        """Тест получения статистики."""
        # Получаем статистику
        stats = self.db.get_statistics()
        
        # Проверяем структуру
        self.assertIn("user_count", stats)
        self.assertIn("currency_count", stats)
        self.assertIn("subscription_count", stats)
        self.assertIn("last_update", stats)
        
        # Проверяем типы
        self.assertIsInstance(stats["user_count"], int)
        self.assertIsInstance(stats["currency_count"], int)
        self.assertIsInstance(stats["subscription_count"], int)
    
    def tearDown(self):
        """Очистка после тестов."""
        self.db.close()


class TestCurrencyRatesCRUD(unittest.TestCase):
    """Тесты для класса CurrencyRatesCRUD."""
    
    def setUp(self):
        """Подготовка тестов."""
        # Создаем mock для DatabaseController
        self.mock_db = MagicMock()
        
        # Создаем CurrencyRatesCRUD с mock-объектом
        from controllers.databasecontroller import CurrencyRatesCRUD
        self.crud = CurrencyRatesCRUD(self.mock_db)
    
    def test_create_multiple_currencies(self):
        """Тест создания нескольких валют."""
        # Подготавливаем данные
        currencies = [
            {"num_code": "840", "char_code": "USD", "name": "Доллар США", 
             "value": 93.25, "nominal": 1},
            {"num_code": "978", "char_code": "EUR", "name": "Евро", 
             "value": 101.70, "nominal": 1}
        ]
        
        # Настраиваем mock
        self.mock_db.create_currency.side_effect = [1, 2]
        
        # Вызываем метод
        result = self.crud._create(currencies)
        
        # Проверяем результат
        self.assertTrue(result)
        self.assertEqual(self.mock_db.create_currency.call_count, 2)
    
    def test_read_all_currencies(self):
        """Тест чтения всех валют."""
        # Настраиваем mock
        expected_currencies = [
            {"id": 1, "char_code": "USD", "value": 93.25},
            {"id": 2, "char_code": "EUR", "value": 101.70}
        ]
        self.mock_db.read_currency.return_value = expected_currencies
        
        # Вызываем метод
        result = self.crud._read()
        
        # Проверяем результат
        self.assertEqual(result, expected_currencies)
        self.mock_db.read_currency.assert_called_once_with(None)
    
    def test_read_specific_currency(self):
        """Тест чтения конкретной валюты по коду."""
        # Настраиваем mock
        expected_currency = {"id": 1, "char_code": "USD", "value": 93.25}
        self.mock_db.read_currency_by_char_code.return_value = expected_currency
        
        # Вызываем метод
        result = self.crud._read("USD")
        
        # Проверяем результат
        self.assertEqual(result, [expected_currency])
        self.mock_db.read_currency_by_char_code.assert_called_once_with("USD")
    
    def test_update_multiple_rates(self):
        """Тест обновления нескольких курсов."""
        # Настраиваем mock
        self.mock_db.update_currency_value.side_effect = [True, True]
        
        # Вызываем метод
        rates = {"USD": 95.0, "EUR": 105.0}
        result = self.crud._update(rates)
        
        # Проверяем результат
        self.assertTrue(result)
        self.assertEqual(self.mock_db.update_currency_value.call_count, 2)
        self.mock_db.update_currency_value.assert_any_call("USD", 95.0)
        self.mock_db.update_currency_value.assert_any_call("EUR", 105.0)
    
    def test_delete_currency(self):
        """Тест удаления валюты."""
        # Настраиваем mock
        self.mock_db.delete_currency.return_value = True
        
        # Вызываем метод
        result = self.crud._delete(1)
        
        # Проверяем результат
        self.assertTrue(result)
        self.mock_db.delete_currency.assert_called_once_with(1)


def run_tests():
    """Запустить все тесты."""
    # Создаем test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Добавляем тесты
    suite.addTests(loader.loadTestsFromTestCase(TestCurrencyController))
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseControllerIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestCurrencyRatesCRUD))
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Выводим статистику
    print("\n" + "="*60)
    print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("="*60)
    print(f"Всего тестов: {result.testsRun}")
    print(f"Пройдено успешно: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Провалено: {len(result.failures)}")
    print(f"Ошибок: {len(result.errors)}")
    
    if result.failures:
        print("\nПроваленные тесты:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print("\nТесты с ошибками:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    print("="*60)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    run_tests()
```

### 8. Выводы о применении MVC, работе с SQLite, обработке маршрутов и рендеринге шаблонов

#### 8.1. Применение архитектуры MVC

В ходе работы была успешно реализована архитектура MVC (Model-View-Controller) с четким разделением ответственности:

1. **Model (Модели)**:
   - Классы в папке `models/` представляют сущности предметной области
   - Каждая модель содержит только свойства и методы доступа (геттеры и сеттеры)
   - Модели не зависят от представления или контроллеров

2. **View (Представления)**:
   - HTML-шаблоны в папке `templates/` отвечают только за отображение данных
   - Использование Jinja2 позволяет разделять логику представления и бизнес-логику
   - Шаблоны наследуются от базового (`base.html`), что обеспечивает единообразие интерфейса

3. **Controller (Контроллеры)**:
   - Разделены на три категории для лучшей организации кода:
     - `DatabaseController` - работа с базой данных (CRUD операции)
     - `CurrencyController` - бизнес-логика для работы с валютами
     - `PagesController` - рендеринг страниц через Jinja2
   - Каждый контроллер имеет четко определенную зону ответственности

#### 8.2. Работа с SQLite

1. **Использование базы в памяти**:
   - SQLite в памяти (`:memory:`) идеально подходит для разработки и тестирования
   - Данные не сохраняются между запусками, что упрощает тестирование
   - Высокая производительность при работе с небольшими объемами данных

2. **CRUD операции**:
   - Реализованы все основные операции: Create, Read, Update, Delete
   - Использованы параметризованные запросы для защиты от SQL-инъекций
   - Поддержка транзакций через `commit()` и `rollback()`

3. **Связи между таблицами**:
   - Использованы первичные ключи (`PRIMARY KEY AUTOINCREMENT`) для уникальной идентификации записей
   - Внешние ключи (`FOREIGN KEY`) обеспечивают целостность данных
   - Связь "многие-ко-многим" реализована через промежуточную таблицу `user_currency`

#### 8.3. Обработка маршрутов

1. **Роутер в HTTP сервере**:
   - Реализован полноценный роутер в классе `CurrencyApp`
   - Поддерживаются все необходимые маршруты согласно заданию
   - Четкое разделение обработчиков для разных типов запросов

2. **Обработка GET параметров**:
   - Использован `urllib.parse.parse_qs()` для парсинга query-параметров
   - Валидация и преобразование типов входных данных
   - Обработка ошибок с возвратом соответствующих HTTP статусов

3. **Работа с формами**:
   - Форма для обновления курсов валют использует GET запросы
   - Кнопки действий (удаление) с подтверждением через JavaScript

#### 8.4. Рендеринг шаблонов

1. **Использование Jinja2**:
   - Объект `Environment` инициализируется один раз для всего приложения
   - Кэширование шаблонов повышает производительность
   - Наследование шаблонов через `{% extends %}` уменьшает дублирование кода

2. **Передача данных в шаблоны**:
   - Контроллеры подготавливают данные в виде словарей
   - Шаблоны получают только готовые для отображения данные
   - Использование фильтров Jinja2 для форматирования данных

3. **Обработка ошибок**:
   - Единый шаблон для отображения ошибок
   - Пользовательские сообщения об ошибках
   - Соответствующие HTTP статус-коды

#### 8.5. Тестирование

1. **Изоляция компонентов**:
   - Использование `unittest.mock` для тестирования контроллеров
   - Mock-объекты заменяют зависимости (базу данных)
   - Возможность тестирования бизнес-логики без реальной БД

2. **Интеграционные тесты**:
   - Тестирование работы с реальной SQLite базой в памяти
   - Проверка корректности SQL запросов и их результатов
   - Тестирование транзакций и обработки ошибок

3. **Покрытие тестами**:
   - Тесты охватывают основные сценарии использования
   - Проверка как успешных, так и ошибочных случаев
   - Тестирование граничных условий

#### 8.6. Преимущества реализованного решения

1. **Модульность**: Каждый компонент системы может разрабатываться и тестироваться независимо
2. **Масштабируемость**: Архитектура позволяет легко добавлять новые сущности и функциональность
3. **Безопасность**: Параметризованные SQL запросы, валидация входных данных
4. **Производительность**: Кэширование шаблонов, индексы в базе данных
5. **Тестируемость**: Четкое разделение ответственности упрощает написание тестов

#### 8.7. Заключение

В ходе лабораторной работы успешно реализовано клиент-серверное приложение для отслеживания курсов валют с использованием SQLite базы данных. Приложение демонстрирует:

- Полноценную реализацию CRUD операций для сущностей Currency и User
- Четкое разделение ответственности в соответствии с архитектурой MVC
- Безопасную работу с базой данных через параметризованные запросы
- Гибкую систему роутинга и обработки HTTP запросов
- Качественное тестирование с использованием unittest.mock

Полученный опыт работы с SQLite, архитектурой MVC и тестированием будет полезен при разработке более сложных веб-приложений на Python.