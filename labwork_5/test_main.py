import unittest
from collections import deque
from main import gen_bin_tree, gen_bin_tree_deque

class TestBinTree(unittest.TestCase):
    
    def test_default_parameters(self):
        """Тест с параметрами по умолчанию"""
        tree = gen_bin_tree()
        self.assertIsInstance(tree, dict)
        self.assertEqual(tree["root"], 6)
        self.assertEqual(tree["root_left"], 10)
        self.assertEqual(tree["root_right"], 10)
    
    def test_custom_height_root(self):
        """Тест с пользовательскими height и root"""
        tree = gen_bin_tree(height=3, root=10)
        self.assertEqual(tree["root"], 10)
        self.assertEqual(tree["root_left"], 18)
        self.assertEqual(tree["root_right"], 14)
    
    def test_custom_branches(self):
        """Тест с пользовательскими функциями ветвления"""
        tree = gen_bin_tree(
            height=2,
            root=5,
            left_branch=lambda r: r + 1,
            right_branch=lambda r: r - 1
        )
        self.assertEqual(tree["root"], 5)
        self.assertEqual(tree["root_left"], 6)
        self.assertEqual(tree["root_right"], 4)
    
    def test_zero_height(self):
        """Тест с нулевой высотой"""
        tree = gen_bin_tree(height=0)
        self.assertIsNone(tree)
    
    def test_height_one(self):
        """Тест с высотой 1 (только корень)"""
        tree = gen_bin_tree(height=1, root=100)
        self.assertEqual(tree, {"root": 100})
    
    def test_deque_version(self):
        """Тест версии с deque"""
        tree = gen_bin_tree_deque(height=2, root=5)
        self.assertIsInstance(tree, deque)
        
        # Преобразуем в список для удобства проверки
        tree_list = list(tree)
        expected_branches = ["root", "root_left", "root_right"]
        expected_values = [5, 8, 9]
        
        for (branch, value), exp_branch, exp_value in zip(tree_list, expected_branches, expected_values):
            self.assertEqual(branch, exp_branch)
            self.assertEqual(value, exp_value)
    
    def test_consistency_between_versions(self):
        """Тест согласованности между двумя версиями"""
        dict_tree = gen_bin_tree(height=3, root=8)
        deque_tree = gen_bin_tree_deque(height=3, root=8)
        
        # Проверяем что оба дерева содержат одинаковые значения
        dict_values = list(dict_tree.values())
        deque_values = [value for _, value in deque_tree]
        
        self.assertEqual(sorted(dict_values), sorted(deque_values))

if __name__ == "__main__":
    unittest.main()