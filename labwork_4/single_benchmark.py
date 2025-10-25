import timeit
from factorial import fact_recursive, fact_iterative

n = 20
recursive_time = timeit.timeit(lambda: fact_recursive(n), number=100000)
iterative_time = timeit.timeit(lambda: fact_iterative(n), number=100000)

print(f"Рекурсивная версия для n={n}: {recursive_time:.6f} сек")
print(f"Итеративная версия для n={n}: {iterative_time:.6f} сек")