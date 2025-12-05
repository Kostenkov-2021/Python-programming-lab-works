import unittest
from unittest.mock import Mock, patch
from demmonstration_example import demonstrate_quadratic




class TestLoggerDecorator(unittest.TestCase):
    """Тесты для декоратора logger."""
    
    def test_logging_to_stdout(self) -> None:
        """Тест логирования в stdout."""
        import io
        from contextlib import redirect_stdout
        
        @logger(handle=sys.stdout)
        def test_func(x: int, y: int) -> int:
            return x + y
        
        with redirect_stdout(io.StringIO()) as f:
            result = test_func(2, 3)
        
        self.assertEqual(result, 5)
        output = f.getvalue()
        self.assertIn("Вызов функции test_func", output)
        self.assertIn("успешно завершилась", output)
        self.assertIn("аргументами: 2, 3", output)
    
    def test_logging_to_stringio(self) -> None:
        """Тест логирования в StringIO."""
        stream = io.StringIO()
        
        @logger(handle=stream)
        def test_func(x: int) -> int:
            return x * 2
        
        result = test_func(5)
        
        self.assertEqual(result, 10)
        logs = stream.getvalue()
        self.assertIn("[INFO]", logs)
        self.assertIn("test_func", logs)
        self.assertIn("аргументами: 5", logs)
        self.assertIn("Результат: 10", logs)
    
    def test_logging_error_to_stringio(self) -> None:
        """Тест логирования ошибок в StringIO."""
        stream = io.StringIO()
        
        @logger(handle=stream)
        def test_func() -> None:
            raise ValueError("Тестовая ошибка")
        
        with self.assertRaises(ValueError):
            test_func()
        
        logs = stream.getvalue()
        self.assertIn("[ERROR]", logs)
        self.assertIn("ValueError", logs)
        self.assertIn("Тестовая ошибка", logs)
    
    def test_logging_to_logger(self) -> None:
        """Тест логирования через logging.Logger."""
        mock_logger = Mock(spec=logging.Logger)
        
        @logger(handle=mock_logger)
        def test_func(a: str, b: int = 10) -> str:
            return f"{a}_{b}"
        
        result = test_func("test", b=20)
        
        self.assertEqual(result, "test_20")
        # Проверяем вызовы info
        self.assertTrue(mock_logger.info.called)
        info_calls = mock_logger.info.call_args_list
        self.assertGreaterEqual(len(info_calls), 2)
        
        # Проверяем, что нет вызовов error
        mock_logger.error.assert_not_called()


class TestGetCurrencies(unittest.TestCase):
    """Тесты для функции get_currencies."""
    
    @patch('requests.get')
    def test_successful_response(self, mock_get: Mock) -> None:
        """Тест успешного получения курсов валют."""
        # Мокаем ответ API
        mock_response = Mock()
        mock_response.json.return_value = {
            'Valute': {
                'USD': {'Value': 93.25, 'Nominal': 1},
                'EUR': {'Value': 101.7, 'Nominal': 1}
            }
        }
        mock_get.return_value = mock_response
        
        result = get_currencies(['USD', 'EUR'])
        
        self.assertEqual(result, {'USD': 93.25, 'EUR': 101.7})
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_currency_not_found(self, mock_get: Mock) -> None:
        """Тест ситуации, когда валюта не найдена."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'Valute': {'USD': {'Value': 93.25}}
        }
        mock_get.return_value = mock_response
        
        with self.assertRaises(KeyError):
            get_currencies(['JPY'])
    
    @patch('requests.get')
    def test_invalid_json(self, mock_get: Mock) -> None:
        """Тест некорректного JSON в ответе."""
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError(
            "Ошибка", "doc", 1
        )
        mock_get.return_value = mock_response
        
        with self.assertRaises(ValueError):
            get_currencies(['USD'])
    
    @patch('requests.get')
    def test_missing_valute_key(self, mock_get: Mock) -> None:
        """Тест отсутствия ключа 'Valute'."""
        mock_response = Mock()
        mock_response.json.return_value = {'data': {}}
        mock_get.return_value = mock_response
        
        with self.assertRaises(KeyError):
            get_currencies(['USD'])
    
    @patch('requests.get')
    def test_invalid_rate_type(self, mock_get: Mock) -> None:
        """Тест некорректного типа курса валюты."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'Valute': {'USD': {'Value': 'не число'}}
        }
        mock_get.return_value = mock_response
        
        with self.assertRaises(TypeError):
            get_currencies(['USD'])
    
    def test_connection_error(self) -> None:
        """Тест ошибки соединения."""
        # Используем несуществующий URL для тестирования ConnectionError
        with self.assertRaises(ConnectionError):
            get_currencies(
                ['USD'],
                url="https://invalid-url-that-does-not-exist.ru"
            )


class TestStreamWrite(unittest.TestCase):
    """Тесты логирования ошибок в поток."""
    
    def setUp(self) -> None:
        """Подготовка тестового окружения."""
        self.stream = io.StringIO()
        
        @logger(handle=self.stream)
        def wrapped() -> Dict[str, float]:
            return get_currencies(['USD'], url="https://invalid-url")
        
        self.wrapped = wrapped
    
    def test_logging_error(self) -> None:
        """Тест логирования ошибки соединения."""
        with self.assertRaises(ConnectionError):
            self.wrapped()
        
        logs = self.stream.getvalue()
        self.assertIn("ERROR", logs)
        self.assertIn("ConnectionError", logs)


class TestSolveQuadratic(unittest.TestCase):
    """Тесты для функции solve_quadratic."""
    
    def test_two_roots(self) -> None:
        """Тест уравнения с двумя корнями."""
        stream = io.StringIO()
        
        @logger(handle=stream)
        def wrapped(a: float, b: float, c: float) -> Optional[Tuple[float, ...]]:
            return solve_quadratic(a, b, c)
        
        result = wrapped(1, -5, 6)
        self.assertEqual(len(result), 2)
        
        logs = stream.getvalue()
        self.assertIn("[INFO]", logs)
        self.assertIn("успешно", logs)
    
    def test_one_root(self) -> None:
        """Тест уравнения с одним корнем."""
        result = solve_quadratic(1, -4, 4)
        self.assertEqual(len(result), 1)
        self.assertAlmostEqual(result[0], 2.0)
    
    def test_no_real_roots(self) -> None:
        """Тест уравнения без действительных корней."""
        result = solve_quadratic(1, 2, 5)
        self.assertIsNone(result)
    
    def test_invalid_coefficients(self) -> None:
        """Тест некорректных коэффициентов."""
        with self.assertRaises(ValueError):
            solve_quadratic("a", 2, 3)
    
    def test_degenerate_equation(self) -> None:
        """Тест вырожденного уравнения."""
        with self.assertRaises(ValueError):
            solve_quadratic(0, 0, 5)


def run_tests() -> None:
    """Запуск всех тестов."""
    # Создаем test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestLoggerDecorator)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestGetCurrencies))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestStreamWrite))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSolveQuadratic))
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print(f"\nРезультаты тестирования:")
    print(f"Пройдено тестов: {result.testsRun - len(result.errors) - len(result.failures)}")
    print(f"Ошибок: {len(result.errors)}")
    print(f"Провалов: {len(result.failures)}")


if __name__ == "__main__":
    # Демонстрация работы
    demonstrate_quadratic()
    show_log_examples()
    
    print("\n" + "=" * 50)
    print("Запуск тестов")
    print("=" * 50)
    run_tests()