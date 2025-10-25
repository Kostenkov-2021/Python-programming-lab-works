import unittest
from main import two_sum

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
    unittest.main()