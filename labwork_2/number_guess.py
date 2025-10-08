import unittest
from unittest.mock import patch
import io
import sys

def guess_number(target, numbers, method='linear'):
    """
    Угадывает число в списке с использованием указанного метода.

    Args:
        target (int): Число, которое нужно угадать.
        numbers (list): Список чисел для поиска.
        method (str): Метод поиска ('linear' или 'binary').

    Returns:
        tuple: Кортеж (угаданное число, количество попыток).
    
    Raises:
        ValueError: Если метод неизвестен или список пуст.
    """
    if not numbers:
        raise ValueError("Список чисел не может быть пустым")

    if method == 'linear':
        return _linear_search(target, numbers)
    elif method == 'binary':
        return _binary_search(target, numbers)
    else:
        raise ValueError("Неизвестный метод. Используйте 'linear' или 'binary'")


def _linear_search(target, numbers):
    """
    Линейный поиск числа в списке.

    Проходится по каждому элементу списка до нахождения целевого числа.
    """
    attempts = 0
    for num in numbers:
        attempts += 1
        if num == target:
            return target, attempts
    raise ValueError("Целевое число отсутствует в списке")


def _binary_search(target, numbers):
    """
    Бинарный поиск числа в отсортированном списке.

    Предварительно сортирует список и выполняет классический бинарный поиск.
    """
    sorted_numbers = sorted(numbers)
    left, right = 0, len(sorted_numbers) - 1
    attempts = 0

    while left <= right:
        mid = (left + right) // 2
        mid_val = sorted_numbers[mid]
        attempts += 1
        
        if mid_val == target:
            return target, attempts
        elif mid_val < target:
            left = mid + 1
        else:
            right = mid - 1
    
    raise ValueError("Целевое число отсутствует в списке")


def input_parameters():
    """
    Вспомогательная функция для ввода параметров с клавиатуры.

    Returns:
        tuple: Кортеж (целевое число, начало диапазона, конец диапазона, метод).
    """
    target = int(input("Введите загаданное число: "))
    start = int(input("Начало диапазона: "))
    end = int(input("Конец диапазона: "))
    method = input("Метод (linear/binary): ").strip().lower()
    
    return target, start, end, method


def main():
    """
    Основная функция программы для поиска числа.
    """
    print("=== Игра 'Угадай число' ===")
    target, start, end, method = input_parameters()
    numbers = list(range(start, end + 1))
    
    try:
        result, attempts = guess_number(target, numbers, method)
        print(f"Число {result} угадано за {attempts} попыток")
    except ValueError as e:
        print(f"Ошибка: {e}")


class TestGuessNumber(unittest.TestCase):
    """Исправленные тесты для функции guess_number."""
    
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

    # ИСПРАВЛЕННЫЕ тесты бинарного поиска
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


def run_tests():
    """Запуск тестов с красивым выводом"""
    print("\n" + "="*60)
    print("ЗАПУСК ТЕСТОВ")
    print("="*60)
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestGuessNumber)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("="*60)
    print(f"РЕЗУЛЬТАТ ТЕСТОВ: {'ВСЕ ТЕСТЫ ПРОЙДЕНЫ' if result.wasSuccessful() else 'ЕСТЬ ОШИБКИ'}")
    print("="*60)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    # Проверяем аргументы командной строки
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # Запуск только тестов
        run_tests()
    elif len(sys.argv) > 1 and sys.argv[1] == 'both':
        # Запуск основной программы и затем тестов
        main()
        run_tests()
    else:
        # Запуск только основной программы (по умолчанию)
        main()
        
        # Спрашиваем пользователя, хочет ли он запустить тесты
        response = input("\nХотите запустить тесты? (y/n): ").strip().lower()
        if response in ['y', 'yes', 'да']:
            run_tests()