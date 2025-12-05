import sys
import io
import logging
import functools
import math
import json
import requests
from typing import Callable, Optional, Any, Union, TextIO, Dict, List, Tuple
from types import TracebackType

# Типы для аннотаций
LoggerType = Union[logging.Logger, TextIO, io.StringIO]
ExcInfo = Union[tuple[type, BaseException, TracebackType], tuple[None, None, None]]


def logger(
    func: Optional[Callable] = None,
    *,
    handle: LoggerType = sys.stdout
) -> Callable:
    """
    Декоратор для логирования вызовов функций с поддержкой разных обработчиков.
    """
    
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            args_repr = [repr(a) for a in args]
            kwargs_repr = [f"{k}={repr(v)}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)
            
            start_msg = f"Вызов функции {f.__name__} с аргументами: {signature}"
            _log_info(start_msg, handle)
            
            try:
                result = f(*args, **kwargs)
                success_msg = f"Функция {f.__name__} успешно завершилась. Результат: {repr(result)}"
                _log_info(success_msg, handle)
                return result
                
            except Exception as e:
                error_msg = f"Ошибка в функции {f.__name__}: {type(e).__name__} - {str(e)}"
                _log_error(error_msg, handle, e)
                raise
        
        return wrapper
    
    if func is None:
        return decorator
    else:
        return decorator(func)


def _log_info(message: str, handle: LoggerType) -> None:
    if isinstance(handle, logging.Logger):
        handle.info(message)
    else:
        handle.write(f"[INFO] {message}\n")


def _log_error(message: str, handle: LoggerType, exc: BaseException) -> None:
    if isinstance(handle, logging.Logger):
        handle.error(message, exc_info=exc)
    else:
        handle.write(f"[ERROR] {message}\n")


@logger(handle=sys.stdout)
def solve_quadratic(a: float, b: float, c: float) -> Optional[Tuple[float, ...]]:
    """
    Решает квадратное уравнение ax² + bx + c = 0.
    """
    try:
        a = float(a)
        b = float(b)
        c = float(c)
    except (TypeError, ValueError) as e:
        raise ValueError(
            f"Коэффициенты должны быть числами. Получено: a={a}, b={b}, c={c}"
        ) from e
    
    if a == 0 and b == 0:
        raise ValueError(
            "Уравнение вырождено: оба коэффициента a и b равны нулю. "
            "Это не квадратное уравнение."
        )
    
    if a == 0:
        if b == 0:
            raise ValueError("Уравнение не имеет решения: b=0")
        root = -c / b
        return (root,)
    
    discriminant = b**2 - 4*a*c
    
    if discriminant < 0:
        return None
    
    sqrt_d = math.sqrt(discriminant)
    root1 = (-b + sqrt_d) / (2*a)
    
    if discriminant == 0:
        return (root1,)
    
    root2 = (-b - sqrt_d) / (2*a)
    return (root1, root2)


def demonstrate_quadratic() -> None:
    """Демонстрация работы solve_quadratic с разными сценариями."""
    print("=" * 50)
    print("Демонстрация решения квадратных уравнений")
    print("=" * 50)
    
    # 1. Два корня (INFO)
    print("\n1. Уравнение с двумя корнями (INFO):")
    print("x² - 5x + 6 = 0")
    result = solve_quadratic(1, -5, 6)
    print(f"Результат: {result}")
    
    # 2. Один корень (INFO)
    print("\n2. Уравнение с одним корнем (INFO):")
    print("x² - 4x + 4 = 0")
    result = solve_quadratic(1, -4, 4)
    print(f"Результат: {result}")
    
    # 3. Нет действительных корней (декоратор логирует возврат None)
    print("\n3. Уравнение без действительных корней:")
    print("x² + 2x + 5 = 0")
    result = solve_quadratic(1, 2, 5)
    print(f"Результат: {result}")
    
    # 4. Ошибка: некорректные данные (ERROR)
    print("\n4. Некорректные данные (ERROR):")
    try:
        solve_quadratic("abc", 2, 3)
    except ValueError:
        print("Ошибка перехвачена")
    
    # 5. Вырожденное уравнение (CRITICAL ситуация)
    print("\n5. Вырожденное уравнение (CRITICAL):")
    try:
        solve_quadratic(0, 0, 5)
    except ValueError:
        print("Ошибка перехвачена")


if __name__ == "__main__":
    demonstrate_quadratic()