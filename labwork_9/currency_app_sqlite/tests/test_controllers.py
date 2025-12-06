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