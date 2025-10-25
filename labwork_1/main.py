def two_sum(nums, target):
    """
    Находит индексы двух чисел в массиве, которые в сумме дают target.
    """
    num_map = {}  # Словарь, хранит число -> индекс
    
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
        print("2 - Выйти")
        
        choice = input("Ваш выбор (1/2): ").strip()
        
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
            print("До свидания!")
            break
            
        else:
            print("Неверный выбор! Пожалуйста, введите 1 или 2.")

if __name__ == '__main__':
    main()