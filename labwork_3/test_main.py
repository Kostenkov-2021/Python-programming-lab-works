import unittest
from main import gen_bin_tree, gen_bin_tree_list, gen_bin_tree_namedtuple


class TestBinaryTree(unittest.TestCase):
    """Тесты для функций генерации бинарного дерева."""
    
    def test_dict_basic(self):
        """Тест базового случая для представления словаря."""
        tree = gen_bin_tree(1, 6)
        expected = {'root': 6, 'left': None, 'right': None}
        self.assertEqual(tree, expected)
    
    def test_dict_height_2(self):
        """Тест дерева высотой 2 для представления словаря."""
        tree = gen_bin_tree(2, 6)
        expected = {
            'root': 6,
            'left': {'root': 10, 'left': None, 'right': None},
            'right': {'root': 10, 'left': None, 'right': None}
        }
        self.assertEqual(tree, expected)
    
    def test_dict_height_3(self):
        """Тест дерева высотой 3 для представления словаря."""
        tree = gen_bin_tree(3, 6)
        
        self.assertEqual(tree['root'], 6)
        self.assertEqual(tree['left']['root'], 10)
        self.assertEqual(tree['right']['root'], 10)
        self.assertEqual(tree['left']['left']['root'], 18)
        self.assertEqual(tree['left']['right']['root'], 14)
    
    def test_dict_default_params(self):
        """Тест с параметрами по умолчанию."""
        tree = gen_bin_tree()
        self.assertIsNotNone(tree)
        self.assertEqual(tree['root'], 6)
    
    def test_dict_invalid_height(self):
        """Тест с некорректной высотой."""
        tree = gen_bin_tree(0, 6)
        self.assertIsNone(tree)
    
    def test_list_representation(self):
        """Тест представления в виде списка."""
        tree = gen_bin_tree_list(2, 6)
        expected = [6, [10, None, None], [10, None, None]]
        self.assertEqual(tree, expected)
    
    def test_namedtuple_representation(self):
        """Тест представления в виде именованного картежа namedtuple."""
        tree = gen_bin_tree_namedtuple(2, 6)
        self.assertEqual(tree.root, 6)
        self.assertEqual(tree.left.root, 10)
        self.assertEqual(tree.right.root, 10)
    
    def test_different_roots(self):
        """Тест с разными значениями корня."""
        tree = gen_bin_tree(2, 10)
        expected = {
            'root': 10,
            'left': {'root': 18, 'left': None, 'right': None},
            'right': {'root': 14, 'left': None, 'right': None}
        }
        self.assertEqual(tree, expected)
    
    def test_consistency_between_representations(self):
        """Тест согласованности между разными представлениями."""
        height = 3
        root = 6
        
        dict_tree = gen_bin_tree(height, root)
        list_tree = gen_bin_tree_list(height, root)
        named_tree = gen_bin_tree_namedtuple(height, root)
        
        # Проверка корней
        self.assertEqual(dict_tree['root'], list_tree[0])
        self.assertEqual(dict_tree['root'], named_tree.root)
        
        # Проверка левых поддеревьев
        self.assertEqual(dict_tree['left']['root'], list_tree[1][0])
        self.assertEqual(dict_tree['left']['root'], named_tree.left.root)
        
        # Проверка правых поддеревьев
        self.assertEqual(dict_tree['right']['root'], list_tree[2][0])
        self.assertEqual(dict_tree['right']['root'], named_tree.right.root)


if __name__ == '__main__':
    unittest.main()