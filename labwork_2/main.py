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


def run_tests():
    """Запуск тестов с красивым выводом"""
    print("\n" + "="*60)
    print("ЗАПУСК ТЕСТОВ")
    print("="*60)
    
    import unittest
    from test_main import TestGuessNumber
    
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