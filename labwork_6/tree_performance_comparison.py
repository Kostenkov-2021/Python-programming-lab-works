import timeit
import matplotlib.pyplot as plt
from typing import Dict, Any, Optional, List
from collections import deque
import random

# Определяем тип узла дерева
TreeNode = Dict[str, Any]

def build_tree_recursive(data: int, height: int, current_height: int = 0) -> Optional[TreeNode]:
    """
    Рекурсивное построение бинарного дерева.
    
    Args:
        data: Значение для текущего узла
        height: Максимальная высота дерева
        current_height: Текущая высота (для рекурсивных вызовов)
    
    Returns:
        Dict, представляющий бинарное дерево, или None если достигнута максимальная высота
    """
    # Базовый случай рекурсии - достигнута максимальная высота
    if current_height >= height:
        return None
    
    # Создаем текущий узел
    node = {
        'value': data,
        'left': None,
        'right': None
    }
    
    # Рекурсивно строим левое и правое поддеревья
    node['left'] = build_tree_recursive(
        data=(data * 2) - 2,  # Левый потомок по формуле варианта
        height=height,
        current_height=current_height + 1
    )
    
    node['right'] = build_tree_recursive(
        data=data + 4,  # Правый потомок по формуле варианта
        height=height,
        current_height=current_height + 1
    )
    
    return node

def build_tree_iterative(root_value: int, height: int) -> Optional[TreeNode]:
    """
    Итеративное построение бинарного дерева с использованием очереди.
    
    Args:
        root_value: Значение корневого узла
        height: Максимальная высота дерева
    
    Returns:
        Dict, представляющий бинарное дерево
    """
    if height <= 0:
        return None
    
    # Создаем корневой узел
    root = {
        'value': root_value,
        'left': None,
        'right': None
    }
    
    # Используем очередь для обхода в ширину
    queue = deque()
    queue.append((root, 0))  # (узел, текущая высота)
    
    while queue:
        current_node, current_height = queue.popleft()
        
        # Если не достигли максимальной высоты, создаем потомков
        if current_height < height - 1:
            # Создаем левого потомка
            left_value = (current_node['value'] * 2) - 2
            current_node['left'] = {
                'value': left_value,
                'left': None,
                'right': None
            }
            queue.append((current_node['left'], current_height + 1))
            
            # Создаем правого потомка
            right_value = current_node['value'] + 4
            current_node['right'] = {
                'value': right_value,
                'left': None,
                'right': None
            }
            queue.append((current_node['right'], current_height + 1))
    
    return root

def count_nodes(tree: Optional[TreeNode]) -> int:
    """
    Подсчитывает количество узлов в дереве.
    
    Args:
        tree: Корень дерева
    
    Returns:
        Количество узлов в дереве
    """
    if tree is None:
        return 0
    
    count = 1
    if tree['left'] is not None:
        count += count_nodes(tree['left'])
    if tree['right'] is not None:
        count += count_nodes(tree['right'])
    
    return count

def compare_performance():
    """
    Сравнивает производительность рекурсивной и итеративной реализации
    для разных высот дерева и строит график результатов.
    """
    # Параметры тестирования
    root_value = 6
    heights = list(range(1, 11))  # Высоты от 1 до 10
    num_runs = 100  # Количество запусков для усреднения
    
    recursive_times = []
    iterative_times = []
    node_counts = []
    
    print("Сравнение производительности построения бинарного дерева:")
    print("Высота | Узлов | Рекурсивное (мс) | Итеративное (мс)")
    print("-" * 50)
    
    for height in heights:
        # Замер времени для рекурсивной реализации
        recursive_time = timeit.timeit(
            lambda: build_tree_recursive(root_value, height),
            number=num_runs
        ) * 1000 / num_runs  # преобразуем в миллисекунды
        
        # Замер времени для итеративной реализации
        iterative_time = timeit.timeit(
            lambda: build_tree_iterative(root_value, height),
            number=num_runs
        ) * 1000 / num_runs  # преобразуем в миллисекунды
        
        # Подсчет узлов для информации
        test_tree = build_tree_iterative(root_value, height)
        nodes = count_nodes(test_tree)
        
        recursive_times.append(recursive_time)
        iterative_times.append(iterative_time)
        node_counts.append(nodes)
        
        print(f"{height:6} | {nodes:5} | {recursive_time:15.4f} | {iterative_time:14.4f}")
    
    # Построение графика
    plt.figure(figsize=(12, 6))
    
    plt.subplot(1, 2, 1)
    plt.plot(heights, recursive_times, 'b-', label='Рекурсивная', linewidth=2, marker='o')
    plt.plot(heights, iterative_times, 'r-', label='Итеративная', linewidth=2, marker='s')
    plt.xlabel('Высота дерева')
    plt.ylabel('Время выполнения (мс)')
    plt.title('Сравнение времени построения дерева')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.subplot(1, 2, 2)
    plt.plot(node_counts, recursive_times, 'b-', label='Рекурсивная', linewidth=2, marker='o')
    plt.plot(node_counts, iterative_times, 'r-', label='Итеративная', linewidth=2, marker='s')
    plt.xlabel('Количество узлов в дереве')
    plt.ylabel('Время выполнения (мс)')
    plt.title('Зависимость времени от количества узлов')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # Анализ результатов
    analyze_results(heights, recursive_times, iterative_times, node_counts)

def analyze_results(heights: List[int], recursive_times: List[float], 
                   iterative_times: List[float], node_counts: List[int]):
    """
    Анализирует результаты сравнения производительности.
    
    Args:
        heights: Список высот деревьев
        recursive_times: Время выполнения рекурсивной реализации
        iterative_times: Время выполнения итеративной реализации
        node_counts: Количество узлов для каждой высоты
    """
    print("\n" + "="*60)
    print("АНАЛИЗ РЕЗУЛЬТАТОВ")
    print("="*60)
    
    # Сравниваем производительность
    faster_count = 0
    slower_count = 0
    
    for i, height in enumerate(heights):
        if recursive_times[i] < iterative_times[i]:
            faster_count += 1
            print(f"Высота {height}: Рекурсивная быстрее на {iterative_times[i] - recursive_times[i]:.4f} мс")
        else:
            slower_count += 1
            print(f"Высота {height}: Итеративная быстрее на {recursive_times[i] - iterative_times[i]:.4f} мс")
    
    print(f"\nСтатистика:")
    print(f"Рекурсивная реализация быстрее в {faster_count} случаях из {len(heights)}")
    print(f"Итеративная реализация быстрее в {slower_count} случаях из {len(heights)}")
    
    # Анализ роста сложности
    print(f"\nАнализ роста времени:")
    print("Высота | Рост рекурсивной | Рост итеративной")
    print("-" * 40)
    
    for i in range(1, len(heights)):
        recursive_growth = recursive_times[i] / recursive_times[i-1] if recursive_times[i-1] > 0 else 0
        iterative_growth = iterative_times[i] / iterative_times[i-1] if iterative_times[i-1] > 0 else 0
        print(f"{heights[i]:6} | {recursive_growth:15.2f} | {iterative_growth:14.2f}")

if __name__ == "__main__":
    # Демонстрация работы функций
    print("Демонстрация построения дерева (высота = 3):")
    
    print("\nРекурсивная реализация:")
    recursive_tree = build_tree_recursive(6, 3)
    print(recursive_tree)
    
    print("\nИтеративная реализация:")
    iterative_tree = build_tree_iterative(6, 3)
    print(iterative_tree)
    
    # Сравнение производительности
    compare_performance()