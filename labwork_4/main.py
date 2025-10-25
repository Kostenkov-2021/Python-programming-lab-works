"""
Основной модуль для запуска бенчмарка и визуализации результатов.
"""
import matplotlib.pyplot as plt
from benchmark import measure_time
from factorial import fact_recursive, fact_iterative


def main() -> None:
    """Основная функция для выполнения сравнения и построения графиков."""
    # Генерируем набор чисел от 0 до 20 для тестирования
    test_numbers = list(range(0, 21))

    # Замеряем время для рекурсивной и итеративной версий
    recursive_times = measure_time(fact_recursive, test_numbers)
    iterative_times = measure_time(fact_iterative, test_numbers)

    # Строим графики
    plt.plot(test_numbers, recursive_times, label="Recursive", marker='o')
    plt.plot(test_numbers, iterative_times, label="Iterative", marker='s')
    plt.xlabel("Input number (n)")
    plt.ylabel("Time (seconds)")
    plt.title("Factorial Computation Time: Recursive vs Iterative")
    plt.legend()
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    main()