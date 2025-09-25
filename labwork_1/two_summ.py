import unittest

def two_sum(nums, target):
    """
    Находит индексы двух чисел в массиве, которые в сумме дают target.
    """
    num_map = {} # Словарь, хранит число -> индекс
    
    for i, num in enumerate(nums):
        complement = target - num

                # Проверяем, есть ли complement в словаре

        if complement in num_map:
            return [num_map[complement], i]
        
                # Добавляем текущее число в словарь

        num_map[num] = i
    
    return []  # Если решение не найдено

def get_user_input():
    """
    Получает ввод от пользователя с клавиатуры.
    """
    print("=== Поиск индексов двух чисел, сумма которых равна target ===")
    
    # Ввод массива чисел
    while True:
        try:
            nums_input = input("Введите массив чисел через пробел (например: 1 2 3 4): ")
            nums = [int(x) for x in nums_input.split()]
            break
        except ValueError:
            print("Ошибка! Пожалуйста, вводите только целые числа, разделенные пробелами.")
    
    # Ввод целевого значения
    while True:
        try:
            target = int(input("Введите целевое значение target: "))
            break
        except ValueError:
            print("Ошибка! Пожалуйста, введите целое число.")
    
    return nums, target

def display_result(nums, target, result):
    """
    Выводит результат на экран.
    """
    print("\n" + "="*50)
    print("РЕЗУЛЬТАТ:")
    print(f"Массив: {nums}")
    print(f"Целевая сумма: {target}")
    
    if result:
        i, j = result
        print(f"Найдены индексы: {result}")
        print(f"Числа: {nums[i]} + {nums[j]} = {nums[i] + nums[j]}")
        print(f"Проверка: {nums[i]} + {nums[j]} = {target}")
    else:
        print("Решение не найдено: нет двух чисел, дающих в сумме target")
    print("="*50)

def main():
    """
    Основная функция программы.
    """
    while True:
        print("\nВыберите режим:")
        print("1 - ввести данные вручную")
        print("2 - Запустить тесты")
        print("3 - Выйти")
        
        choice = input("Ваш выбор (1/2/3): ").strip()
        
        if choice == '1':
            # Режим ввода с клавиатуры
            nums, target = get_user_input()
            result = two_sum(nums, target)
            display_result(nums, target, result)
            
            # Предложение повторить
            repeat = input("\nХотите выполнить еще один поиск? (y/n): ").strip().lower()
            if repeat != 'y':
                print("До свидания!")
                break
                
        elif choice == '2':
            # Режим запуска тестов
            print("\nЗапуск тестов...")
            unittest.main(argv=[''], exit=False, verbosity=2)
            
        elif choice == '3':
            print("До свидания!")
            break
            
        else:
            print("Неверный выбор! Пожалуйста, введите 1, 2 или 3.")

# Тесты с использованием unittest

class TestTwoSum(unittest.TestCase):
    
    def test_example1(self):
        nums = [2, 7, 11, 15]
        target = 9
        result = two_sum(nums, target)
        self.assertEqual(sorted(result), [0, 1])
    
    def test_example2(self):
        nums = [3, 2, 4]
        target = 6
        result = two_sum(nums, target)
        self.assertEqual(sorted(result), [1, 2])
    
    def test_example3(self):
        nums = [3, 3]
        target = 6
        result = two_sum(nums, target)
        self.assertEqual(sorted(result), [0, 1])
    
    def test_empty_array(self):
        nums = []
        target = 5
        result = two_sum(nums, target)
        self.assertEqual(result, [])
    
    def test_single_element(self):
        nums = [5]
        target = 5
        result = two_sum(nums, target)
        self.assertEqual(result, [])

    def test_no_solution(self):
        nums = [1, 2, 3, 4]
        target = 10
        result = two_sum(nums, target)
        self.assertEqual(result, [])
    
    def test_negative_numbers(self):
        nums = [-1, -2, -3, -4]
        target = -5
        result = two_sum(nums, target)
        self.assertEqual(sorted(result), [1, 2])
    
    def test_mixed_positive_negative(self):
        nums = [-1, 2, 3, -4]
        target = 1
        result = two_sum(nums, target)
        self.assertEqual(sorted(result), [0, 1])
    
    def test_zero_target(self):
        nums = [-1, 1, 2, 3]
        target = 0
        result = two_sum(nums, target)
        self.assertEqual(sorted(result), [0, 1])
    
    def test_large_numbers(self):
        nums = [1000000, 2000000, 3000000]
        target = 5000000
        result = two_sum(nums, target)
        self.assertEqual(sorted(result), [1, 2])
    
    def test_duplicate_numbers_valid(self):
        nums = [1, 2, 2, 3]
        target = 4
        result = two_sum(nums, target)
        self.assertEqual(sorted(result), [1, 2])
    
    def test_duplicate_numbers_invalid(self):
        nums = [1, 1, 1, 1]
        target = 3
        result = two_sum(nums, target)
        self.assertEqual(result, [])
    
    def test_consecutive_numbers(self):
        nums = [1, 2, 3, 4, 5]
        target = 9
        result = two_sum(nums, target)
        self.assertEqual(sorted(result), [3, 4])
    
    def test_first_last_elements(self):
        nums = [10, 2, 3, 4, 5]
        target = 15
        result = two_sum(nums, target)
        self.assertEqual(sorted(result), [0, 4])
    
    def test_identical_elements_valid(self):
        nums = [3, 3]
        target = 6
        result = two_sum(nums, target)
        self.assertEqual(sorted(result), [0, 1])
    
    def test_identical_elements_invalid(self):
        nums = [3, 3, 3]
        target = 10
        result = two_sum(nums, target)
        self.assertEqual(result, [])
    
    def test_negative_target(self):
        nums = [1, -2, 3, -4]
        target = -1
        result = two_sum(nums, target)
        self.assertEqual(sorted(result), [0, 1])
    
    def test_large_array(self):
        nums = list(range(1, 1001))
        target = 1999  # 1000 + 999
        result = two_sum(nums, target)
        self.assertEqual(sorted(result), [998, 999])
    
    def test_zero_in_array(self):
        nums = [0, 4, 3, 0]
        target = 0
        result = two_sum(nums, target)
        self.assertEqual(sorted(result), [0, 3])
    
    def test_same_element_twice_invalid(self):
        nums = [3, 2, 4]
        target = 6
        result = two_sum(nums, target)
        self.assertNotEqual(result, [0, 0])
        self.assertNotEqual(result, [1, 1])
        self.assertNotEqual(result, [2, 2])
    
    def test_order_independence(self):
        nums = [4, 2, 3, 1]
        target = 5
        result1 = two_sum(nums, target)
        self.assertEqual(sorted(result1), [1, 2])
        
        nums_reversed = [1, 3, 2, 4]
        result2 = two_sum(nums_reversed, target)
        self.assertEqual(sorted(result2), [1, 2])

if __name__ == '__main__':
    main()