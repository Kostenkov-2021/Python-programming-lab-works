"""
Тесты для моделей приложения.
"""

import unittest
import sys
import os

# Добавляем путь для импорта модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Author, App, User, Currency, UserCurrency
from datetime import datetime


class TestAuthorModel(unittest.TestCase):
    """Тесты для модели Author."""
    
    def setUp(self):
        """Подготовка тестов."""
        self.author = Author("Иван Иванов", "ПИ-202")
    
    def test_author_creation(self):
        """Тест создания автора."""
        self.assertEqual(self.author.name, "Иван Иванов")
        self.assertEqual(self.author.group, "ПИ-202")
    
    def test_name_setter_validation(self):
        """Тест валидации имени."""
        with self.assertRaises(TypeError):
            self.author.name = 123
        
        with self.assertRaises(ValueError):
            self.author.name = ""
        
        with self.assertRaises(ValueError):
            self.author.name = "   "
    
    def test_group_setter_validation(self):
        """Тест валидации группы."""
        with self.assertRaises(TypeError):
            self.author.group = 456
        
        with self.assertRaises(ValueError):
            self.author.group = ""
    
    def test_to_dict(self):
        """Тест преобразования в словарь."""
        data = self.author.to_dict()
        self.assertEqual(data['name'], "Иван Иванов")
        self.assertEqual(data['group'], "ПИ-202")
    
    def test_str_representation(self):
        """Тест строкового представления."""
        self.assertEqual(str(self.author), "Иван Иванов (ПИ-202)")


class TestAppModel(unittest.TestCase):
    """Тесты для модели App."""
    
    def setUp(self):
        """Подготовка тестов."""
        self.author = Author("Иван Иванов", "ПИ-202")
        self.app = App("Currency Tracker", "1.0.0", self.author)
    
    def test_app_creation(self):
        """Тест создания приложения."""
        self.assertEqual(self.app.name, "Currency Tracker")
        self.assertEqual(self.app.version, "1.0.0")
        self.assertEqual(self.app.author, self.author)
    
    def test_name_setter_validation(self):
        """Тест валидации названия."""
        with self.assertRaises(TypeError):
            self.app.name = 123
        
        with self.assertRaises(ValueError):
            self.app.name = ""
    
    def test_version_setter_validation(self):
        """Тест валидации версии."""
        with self.assertRaises(TypeError):
            self.app.version = 1.0
        
        with self.assertRaises(ValueError):
            self.app.version = "1.0"
        
        with self.assertRaises(ValueError):
            self.app.version = "1.0.a"
        
        # Корректная версия
        self.app.version = "2.1.3"
        self.assertEqual(self.app.version, "2.1.3")
    
    def test_author_setter_validation(self):
        """Тест валидации автора."""
        with self.assertRaises(TypeError):
            self.app.author = "Иван Иванов"
    
    def test_to_dict(self):
        """Тест преобразования в словарь."""
        data = self.app.to_dict()
        self.assertEqual(data['name'], "Currency Tracker")
        self.assertEqual(data['version'], "1.0.0")
        self.assertEqual(data['author']['name'], "Иван Иванов")


class TestUserModel(unittest.TestCase):
    """Тесты для модели User."""
    
    def setUp(self):
        """Подготовка тестов."""
        self.user = User(1, "Иван Иванов")
    
    def test_user_creation(self):
        """Тест создания пользователя."""
        self.assertEqual(self.user.id, 1)
        self.assertEqual(self.user.name, "Иван Иванов")
        self.assertEqual(len(self.user.subscriptions), 0)
    
    def test_id_setter_validation(self):
        """Тест валидации ID."""
        with self.assertRaises(TypeError):
            self.user.id = "один"
        
        with self.assertRaises(ValueError):
            self.user.id = 0
        
        with self.assertRaises(ValueError):
            self.user.id = -1
        
        # Корректный ID
        self.user.id = 100
        self.assertEqual(self.user.id, 100)
    
    def test_name_setter_validation(self):
        """Тест валидации имени."""
        with self.assertRaises(TypeError):
            self.user.name = 123
        
        with self.assertRaises(ValueError):
            self.user.name = ""
        
        # Имя с пробелами должно обрезаться
        self.user.name = "  Петр Петров  "
        self.assertEqual(self.user.name, "Петр Петров")
    
    def test_subscription_management(self):
        """Тест управления подписками."""
        # Добавление подписки
        subscription = self.user.subscribe_to_currency("R01235")
        self.assertEqual(len(self.user.subscriptions), 1)
        self.assertEqual(subscription.user_id, 1)
        self.assertEqual(subscription.currency_id, "R01235")
        
        # Нельзя добавить дублирующую подписку
        with self.assertRaises(ValueError):
            self.user.subscribe_to_currency("R01235")
        
        # Добавление второй подписки
        self.user.subscribe_to_currency("R01239")
        self.assertEqual(len(self.user.subscriptions), 2)
        
        # Получение ID подписок
        currency_ids = self.user.get_subscribed_currency_ids()
        self.assertIn("R01235", currency_ids)
        self.assertIn("R01239", currency_ids)
        
        # Проверка подписки
        self.assertTrue(self.user.has_subscription("R01235"))
        self.assertFalse(self.user.has_subscription("R99999"))
        
        # Удаление подписки
        result = self.user.unsubscribe_from_currency("R01235")
        self.assertTrue(result)
        self.assertEqual(len(self.user.subscriptions), 1)
        self.assertFalse(self.user.has_subscription("R01235"))
        
        # Удаление несуществующей подписки
        result = self.user.unsubscribe_from_currency("R99999")
        self.assertFalse(result)
    
    def test_to_dict(self):
        """Тест преобразования в словарь."""
        self.user.subscribe_to_currency("R01235")
        
        # С подписками
        data_with_subs = self.user.to_dict(include_subscriptions=True)
        self.assertEqual(data_with_subs['id'], 1)
        self.assertEqual(data_with_subs['name'], "Иван Иванов")
        self.assertEqual(len(data_with_subs['subscriptions']), 1)
        self.assertIn('R01235', data_with_subs['subscribed_currencies'])
        
        # Без подписок
        data_without_subs = self.user.to_dict(include_subscriptions=False)
        self.assertEqual(data_without_subs['id'], 1)
        self.assertEqual(data_without_subs['name'], "Иван Иванов")
        self.assertNotIn('subscriptions', data_without_subs)


class TestCurrencyModel(unittest.TestCase):
    """Тесты для модели Currency."""
    
    def setUp(self):
        """Подготовка тестов."""
        self.currency = Currency(
            currency_id="R01235",
            num_code="840",
            char_code="USD",
            name="Доллар США",
            value=93.25,
            nominal=1
        )
    
    def test_currency_creation(self):
        """Тест создания валюты."""
        self.assertEqual(self.currency.id, "R01235")
        self.assertEqual(self.currency.num_code, "840")
        self.assertEqual(self.currency.char_code, "USD")
        self.assertEqual(self.currency.name, "Доллар США")
        self.assertEqual(self.currency.value, 93.25)
        self.assertEqual(self.currency.nominal, 1)
        self.assertIsInstance(self.currency.last_updated, datetime)
    
    def test_id_setter_validation(self):
        """Тест валидации ID."""
        with self.assertRaises(TypeError):
            self.currency.id = 123
        
        with self.assertRaises(ValueError):
            self.currency.id = ""
    
    def test_num_code_setter_validation(self):
        """Тест валидации цифрового кода."""
        with self.assertRaises(TypeError):
            self.currency.num_code = 840
        
        with self.assertRaises(ValueError):
            self.currency.num_code = "84"
        
        with self.assertRaises(ValueError):
            self.currency.num_code = "84A"
        
        # Корректный код
        self.currency.num_code = "978"
        self.assertEqual(self.currency.num_code, "978")
    
    def test_char_code_setter_validation(self):
        """Тест валидации символьного кода."""
        with self.assertRaises(TypeError):
            self.currency.char_code = 123
        
        with self.assertRaises(ValueError):
            self.currency.char_code = "US"
        
        with self.assertRaises(ValueError):
            self.currency.char_code = "USDX"
        
        # Код должен быть в верхнем регистре
        self.currency.char_code = "eur"
        self.assertEqual(self.currency.char_code, "EUR")
    
    def test_value_setter_validation(self):
        """Тест валидации курса."""
        with self.assertRaises(TypeError):
            self.currency.value = "сто"
        
        with self.assertRaises(ValueError):
            self.currency.value = -10.0
        
        # Можно передавать int
        self.currency.value = 100
        self.assertEqual(self.currency.value, 100.0)
    
    def test_nominal_setter_validation(self):
        """Тест валидации номинала."""
        with self.assertRaises(TypeError):
            self.currency.nominal = "один"
        
        with self.assertRaises(ValueError):
            self.currency.nominal = 0
        
        # Корректный номинал
        self.currency.nominal = 100
        self.assertEqual(self.currency.nominal, 100)
    
    def test_get_value_for_nominal(self):
        """Тест расчета курса для произвольного номинала."""
        self.currency.value = 93.25
        self.currency.nominal = 1
        
        # Для номинала 1
        self.assertEqual(self.currency.get_value_for_nominal(1), 93.25)
        
        # Для номинала 10
        self.assertEqual(self.currency.get_value_for_nominal(10), 932.5)
        
        # Для номинала 0.5
        self.assertEqual(self.currency.get_value_for_nominal(0.5), 46.625)
        
        # Ошибка при отрицательном номинале
        with self.assertRaises(ValueError):
            self.currency.get_value_for_nominal(-1)
    
    def test_to_dict(self):
        """Тест преобразования в словарь."""
        data = self.currency.to_dict()
        self.assertEqual(data['id'], "R01235")
        self.assertEqual(data['num_code'], "840")
        self.assertEqual(data['char_code'], "USD")
        self.assertEqual(data['name'], "Доллар США")
        self.assertEqual(data['value'], 93.25)
        self.assertEqual(data['nominal'], 1)
        self.assertEqual(data['value_per_unit'], 93.25)


class TestUserCurrencyModel(unittest.TestCase):
    """Тесты для модели UserCurrency."""
    
    def setUp(self):
        """Подготовка тестов."""
        self.subscription = UserCurrency(1, 1, "R01235")
    
    def test_subscription_creation(self):
        """Тест создания подписки."""
        self.assertEqual(self.subscription.id, 1)
        self.assertEqual(self.subscription.user_id, 1)
        self.assertEqual(self.subscription.currency_id, "R01235")
    
    def test_id_setter_validation(self):
        """Тест валидации ID подписки."""
        with self.assertRaises(TypeError):
            self.subscription.id = "один"
        
        with self.assertRaises(ValueError):
            self.subscription.id = 0
    
    def test_user_id_setter_validation(self):
        """Тест валидации ID пользователя."""
        with self.assertRaises(TypeError):
            self.subscription.user_id = "один"
        
        with self.assertRaises(ValueError):
            self.subscription.user_id = 0
    
    def test_currency_id_setter_validation(self):
        """Тест валидации ID валюты."""
        with self.assertRaises(TypeError):
            self.subscription.currency_id = 123
        
        with self.assertRaises(ValueError):
            self.subscription.currency_id = ""
    
    def test_to_dict(self):
        """Тест преобразования в словарь."""
        data = self.subscription.to_dict()
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['user_id'], 1)
        self.assertEqual(data['currency_id'], "R01235")


class TestModelRelations(unittest.TestCase):
    """Тесты связей между моделями."""
    
    def test_user_currency_relation(self):
        """Тест связи пользователя с валютой."""
        user = User(1, "Иван Иванов")
        currency = Currency("R01235", "840", "USD", "Доллар США", 93.25, 1)
        
        # Пользователь подписывается на валюту
        subscription = user.subscribe_to_currency(currency.id)
        
        # Проверяем связь
        self.assertEqual(subscription.user_id, user.id)
        self.assertEqual(subscription.currency_id, currency.id)
        
        # Пользователь должен иметь эту подписку
        self.assertTrue(user.has_subscription(currency.id))
        
        # Удаляем подписку
        user.unsubscribe_from_currency(currency.id)
        self.assertFalse(user.has_subscription(currency.id))


if __name__ == '__main__':
    unittest.main(verbosity=2)