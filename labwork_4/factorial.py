"""
Модуль с реализациями вычисления факториала.
"""

def fact_recursive(n: int) -> int:
    """
    Вычисляет факториал числа n рекурсивным методом.

    Args:
        n: Натуральное число (0 <= n <= 997 для избежания переполнения стека).

    Returns:
        Факториал числа n.

    Raises:
        ValueError: Если n < 0.
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    if n == 0:
        return 1
    return n * fact_recursive(n - 1)


def fact_iterative(n: int) -> int:
    """
    Вычисляет факториал числа n итеративным методом.

    Args:
        n: Натуральное число.

    Returns:
        Факториал числа n.

    Raises:
        ValueError: Если n < 0.
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result