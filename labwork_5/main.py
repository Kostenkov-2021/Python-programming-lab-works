from collections import deque
from typing import Any, Callable, Optional, Union

def gen_bin_tree(
    height: int = 5,
    root: int = 6,
    left_branch: Callable[[int], int] = lambda r: r * 2 - 2,
    right_branch: Callable[[int], int] = lambda r: r + 4
) -> Optional[dict]:
    """
    Генерирует бинарное дерево с заданными параметрами.
    
    Args:
        height: Высота дерева (количество уровней). По умолчанию 5.
        root: Значение корневого узла. По умолчанию 6.
        left_branch: Функция для вычисления левого потомка. По умолчанию (root*2)-2.
        right_branch: Функция для вычисления правого потомка. По умолчанию root+4.
    
    Returns:
        Словарь, представляющий структуру дерева, или None если высота равна 0.
    
    Examples:
        >>> tree = gen_bin_tree(height=3, root=5)
        >>> print(tree)
    """
    if height <= 0:
        return None
    
    tree = {}
    stack = deque()
    stack.append((0, root, "root", None))
    
    while stack:
        level, value, branch, parent = stack.pop()
        
        # Формируем ключ для текущего узла
        if parent is None:
            key = "root"
        else:
            key = f"{parent}_{branch}"
        
        # Добавляем узел в дерево
        tree[key] = value
        
        # Если не достигли максимальной глубины, добавляем потомков
        if level + 1 < height:
            left_val = left_branch(value)
            right_val = right_branch(value)
            
            # Сначала добавляем правого потомка (чтобы левый обработался первым)
            stack.append((level + 1, right_val, "right", key))
            stack.append((level + 1, left_val, "left", key))
    
    return tree

def gen_bin_tree_deque(
    height: int = 5,
    root: int = 6,
    left_branch: Callable[[int], int] = lambda r: r * 2 - 2,
    right_branch: Callable[[int], int] = lambda r: r + 4
) -> Optional[deque]:
    """
    Генерирует бинарное дерево с использованием deque из collections.
    
    Args:
        height: Высота дерева. По умолчанию 5.
        root: Значение корневого узла. По умолчанию 6.
        left_branch: Функция для вычисления левого потомка. По умолчанию (root*2)-2.
        right_branch: Функция для вычисления правого потомка. По умолчанию root+4.
    
    Returns:
        deque, представляющий структуру дерева в порядке уровней, или None если высота равна 0.
    """
    if height <= 0:
        return None
    
    tree = deque()
    current_level = deque([("root", root)])
    
    for level in range(height):
        next_level = deque()
        
        for branch, value in current_level:
            tree.append((branch, value))
            
            if level + 1 < height:
                left_val = left_branch(value)
                right_val = right_branch(value)
                
                next_level.append((f"{branch}_left", left_val))
                next_level.append((f"{branch}_right", right_val))
        
        current_level = next_level
    
    return tree

if __name__ == "__main__":
    # Пример использования
    tree_dict = gen_bin_tree()
    print("Дерево как словарь:")
    print(tree_dict)
    
    tree_deque = gen_bin_tree_deque()
    print("\nДерево как deque:")
    for branch, value in tree_deque:
        print(f"{branch}: {value}")