import unittest
from unittest.mock import patch
import io
import sys
from main import guess_number, input_parameters, main


class TestGuessNumber(unittest.TestCase):
    """Тесты для функции guess_number."""
    
    # Тесты линейного поиска
    def test_linear_search_first_element(self):
        numbers = [1, 2, 3, 4, 5]
        self.assertEqual(guess_number(1, numbers, 'linear'), (1, 1))

    def test_linear_search_last_element(self):
        numbers = [1, 2, 3, 4, 5]
        self.assertEqual(guess_number(5, numbers, 'linear'), (5, 5))

    def test_linear_search_middle_element(self):
        numbers = [1, 2, 3, 4, 5]
        self.assertEqual(guess_number(3, numbers, 'linear'), (3, 3))

    def test_linear_search_duplicates(self):
        numbers = [1, 2, 2, 3, 4]
        self.assertEqual(guess_number(2, numbers, 'linear'), (2, 2))

    def test_linear_search_negative_numbers(self):
        numbers = [-5, -3, 0, 1, 4]
        self.assertEqual(guess_number(-3, numbers, 'linear'), (-3, 2))

    # Тесты бинарного поиска
    def test_binary_search_sorted(self):
        numbers = [1, 2, 3, 4, 5]
        self.assertEqual(guess_number(3, numbers, 'binary'), (3, 1))

    def test_binary_search_unsorted(self):
        numbers = [5, 2, 8, 1, 9]
        self.assertEqual(guess_number(8, numbers, 'binary'), (8, 2))

    def test_binary_search_first_element(self):
        numbers = [1, 2, 3, 4, 5]
        self.assertEqual(guess_number(1, numbers, 'binary'), (1, 2))

    def test_binary_search_last_element(self):
        numbers = [1, 2, 3, 4, 5]
        self.assertEqual(guess_number(5, numbers, 'binary'), (5, 3))

    def test_binary_search_duplicates(self):
        numbers = [1, 2, 2, 3, 4]
        result, attempts = guess_number(2, numbers, 'binary')
        self.assertEqual(result, 2)
        self.assertLessEqual(attempts, 2)

    def test_binary_search_negative_numbers(self):
        numbers = [-5, -3, 0, 1, 4]
        self.assertEqual(guess_number(-3, numbers, 'binary'), (-3, 3))

    # Тесты на особые случаи
    def test_single_element_found(self):
        numbers = [42]
        self.assertEqual(guess_number(42, numbers, 'linear'), (42, 1))
        self.assertEqual(guess_number(42, numbers, 'binary'), (42, 1))

    def test_single_element_not_found(self):
        numbers = [10]
        with self.assertRaises(ValueError):
            guess_number(5, numbers, 'linear')
        with self.assertRaises(ValueError):
            guess_number(5, numbers, 'binary')

    def test_empty_list(self):
        with self.assertRaises(ValueError) as context:
            guess_number(1, [], 'linear')
        self.assertEqual(str(context.exception), "Список чисел не может быть пустым")

    def test_invalid_method(self):
        with self.assertRaises(ValueError) as context:
            guess_number(1, [1, 2, 3], 'invalid')
        self.assertEqual(str(context.exception), "Неизвестный метод. Используйте 'linear' или 'binary'")

    # Тесты на отсутствующие элементы
    def test_number_not_in_list_linear(self):
        numbers = [1, 2, 3, 4, 5]
        with self.assertRaises(ValueError) as context:
            guess_number(10, numbers, 'linear')
        self.assertEqual(str(context.exception), "Целевое число отсутствует в списке")

    def test_number_not_in_list_binary(self):
        numbers = [1, 2, 3, 4, 5]
        with self.assertRaises(ValueError) as context:
            guess_number(10, numbers, 'binary')
        self.assertEqual(str(context.exception), "Целевое число отсутствует в списке")

    # Тесты производительности
    def test_large_list_linear(self):
        numbers = list(range(1, 1001))
        result, attempts = guess_number(999, numbers, 'linear')
        self.assertEqual(result, 999)
        self.assertEqual(attempts, 999)

    def test_large_list_binary(self):
        numbers = list(range(1, 1001))
        result, attempts = guess_number(999, numbers, 'binary')
        self.assertEqual(result, 999)
        self.assertLess(attempts, 15)

    # Тест с нулевыми значениями
    def test_zero_values(self):
        numbers = [0, 0, 0, 1, 2]
        self.assertEqual(guess_number(0, numbers, 'linear'), (0, 1))
        result, attempts = guess_number(0, numbers, 'binary')
        self.assertEqual(result, 0)
        self.assertEqual(attempts, 1)

    # Тест методов по умолчанию
    def test_default_method(self):
        numbers = [1, 2, 3, 4, 5]
        self.assertEqual(guess_number(3, numbers), (3, 3))

    # Тесты ввода параметров
    @patch('builtins.input', side_effect=['5', '1', '10', 'linear'])
    def test_input_parameters(self, mock_input):
        target, start, end, method = input_parameters()
        self.assertEqual(target, 5)
        self.assertEqual(start, 1)
        self.assertEqual(end, 10)
        self.assertEqual(method, 'linear')

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('builtins.input', side_effect=['5', '1', '10', 'binary'])
    def test_main_execution_success(self, mock_input, mock_stdout):
        main()
        output = mock_stdout.getvalue()
        self.assertIn("Число 5 угадано за", output)

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('builtins.input', side_effect=['15', '1', '10', 'linear'])
    def test_main_execution_failure(self, mock_input, mock_stdout):
        main()
        output = mock_stdout.getvalue()
        self.assertIn("Ошибка: Целевое число отсутствует в списке", output)


if __name__ == '__main__':
    unittest.main()