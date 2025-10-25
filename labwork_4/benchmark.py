"""
Модуль для замера времени выполнения функций.
"""
import timeit
from typing import Callable, List
from factorial import fact_recursive, fact_iterative


def measure_time(func: Callable[[int], int], numbers: List[int]) -> List[float]:
    """
    Замеряет среднее время выполнения функции на заданных числах.

    Args:
        func: Функция, принимающая int и возвращающая int.
        numbers: Список чисел для тестирования.

    Returns:
        Список средних времен выполнения в секундах для каждого числа.
    """
    times = []
    for n in numbers:
        # Используем timeit для замера времени с 100000 прогонами для усреднения
        timer = timeit.Timer(lambda: func(n))
        # Выполняем 5 запусков по 100000 итераций, берём минимальное время
        time_taken = min(timer.repeat(repeat=5, number=100000))
        times.append(time_taken)
    return times