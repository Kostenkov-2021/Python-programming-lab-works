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