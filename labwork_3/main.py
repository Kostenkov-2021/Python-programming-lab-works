from collections import namedtuple
from typing import Optional


def gen_bin_tree(height: int = 5, root: int = 6) -> Optional[dict]:
    """
    Рекурсивно генерирует бинарное дерево в виде словаря.
    
    Args:
        height: Высота дерева (количество уровней). Должна быть >= 1.
        root: Значение корневого узла.
        
    Returns:
        Словарь, представляющий бинарное дерево, где каждый узел имеет форму:
        {
            'root': value,
            'left': left_subtree,
            'right': right_subtree
        }
        или None если высота меньше 1.
        
    Raises:
        ValueError: Если высота меньше 1.
        
    Examples:
        >>> tree = gen_bin_tree(2, 1)
        >>> tree['root']
        1
    """
    if height < 1:
        return None
    if height == 1:
        return {'root': root, 'left': None, 'right': None}
    
    left_child = (root * 2) - 2
    right_child = root + 4
    
    return {
        'root': root,
        'left': gen_bin_tree(height - 1, left_child),
        'right': gen_bin_tree(height - 1, right_child)
    }


def gen_bin_tree_list(height: int = 5, root: int = 6) -> Optional[list]:
    """
    Рекурсивно генерирует бинарное дерево в виде списка (представление в виде кучи).
    
    Args:
        height: Высота дерева (количество уровней). Должна быть >= 1.
        root: Значение корневого узла.
        
    Returns:
        Список, представляющий бинарное дерево в виде кучи, где:
        - index 0: корень
        - index 1: левое поддерево
        - index 2: правое поддерево
        или None если высота меньше 1.
    """
    if height < 1:
        return None
    if height == 1:
        return [root, None, None]
    
    left_child = (root * 2) - 2
    right_child = root + 4
    
    return [
        root,
        gen_bin_tree_list(height - 1, left_child),
        gen_bin_tree_list(height - 1, right_child)
    ]


def gen_bin_tree_namedtuple(height: int = 5, root: int = 6) -> Optional[object]:
    """
    Рекурсивно генерирует бинарное дерево с использованием namedtuple.
    
    Args:
        height: Высота дерева (количество уровней). Должна быть >= 1.
        root: Значение корневого узла.
        
    Returns:
        Объект Node с полями root, left, right или None если высота меньше 1.
    """
    if height < 1:
        return None
    
    Node = namedtuple('Node', ['root', 'left', 'right'])
    
    if height == 1:
        return Node(root, None, None)
    
    left_child = (root * 2) - 2
    right_child = root + 4
    
    return Node(
        root,
        gen_bin_tree_namedtuple(height - 1, left_child),
        gen_bin_tree_namedtuple(height - 1, right_child)
    )


def demonstrate_trees():
    """Демонстрация работы всех функций генерации деревьев."""
    print("Дерево в виде словаря (высота 3):")
    tree_dict = gen_bin_tree(3, 6)
    print(tree_dict)
    
    print("\nДерево в виде списка (высота 3):")
    tree_list = gen_bin_tree_list(3, 6)
    print(tree_list)
    
    print("\nДерево в виде namedtuple (высота 3):")
    tree_named = gen_bin_tree_namedtuple(3, 6)
    print(tree_named)


def run_tests():
    """Запуск тестов."""
    print("\nЗапуск тестов...")
    import unittest
    from test_main import TestBinaryTree
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestBinaryTree)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    # Демонстрация работы
    demonstrate_trees()
    
    # Спрашиваем пользователя, хочет ли он запустить тесты
    response = input("\nХотите запустить тесты? (y/n): ").strip().lower()
    if response in ['y', 'yes', 'да']:
        run_tests()