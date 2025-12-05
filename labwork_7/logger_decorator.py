import sys
import io
import logging
import functools
from typing import Callable, Optional, Any, Union, TextIO
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
    
    Args:
        func: Декорируемая функция (используется при вызове без скобок)
        handle: Объект для логирования. Может быть:
            - logging.Logger: логирование через методы info()/error()
            - io.StringIO/TextIO: логирование через метод write()
    
    Returns:
        Декорированную функцию с добавленным логированием
        
    Examples:
        >>> @logger
        ... def func(): ...
        
        >>> @logger(handle=io.StringIO())
        ... def func(): ...
        
        >>> @logger(handle=logging.getLogger("app"))
        ... def func(): ...
    """
    
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Формируем строку аргументов для логирования
            args_repr = [repr(a) for a in args]
            kwargs_repr = [f"{k}={repr(v)}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)
            
            # Логируем начало вызова
            start_msg = f"Вызов функции {f.__name__} с аргументами: {signature}"
            _log_info(start_msg, handle)
            
            try:
                result = f(*args, **kwargs)
                # Логируем успешное завершение
                success_msg = f"Функция {f.__name__} успешно завершилась. Результат: {repr(result)}"
                _log_info(success_msg, handle)
                return result
                
            except Exception as e:
                # Логируем ошибку
                error_msg = f"Ошибка в функции {f.__name__}: {type(e).__name__} - {str(e)}"
                _log_error(error_msg, handle, e)
                raise
        
        return wrapper
    
    # Обработка вызова декоратора с аргументами и без
    if func is None:
        return decorator
    else:
        return decorator(func)


def _log_info(message: str, handle: LoggerType) -> None:
    """
    Вспомогательная функция для логирования информационных сообщений.
    
    Args:
        message: Сообщение для логирования
        handle: Объект для логирования
    """
    if isinstance(handle, logging.Logger):
        handle.info(message)
    else:
        handle.write(f"[INFO] {message}\n")


def _log_error(message: str, handle: LoggerType, exc: BaseException) -> None:
    """
    Вспомогательная функция для логирования сообщений об ошибках.
    
    Args:
        message: Сообщение для логирования
        handle: Объект для логирования
        exc: Исключение
    """
    if isinstance(handle, logging.Logger):
        handle.error(message, exc_info=exc)
    else:
        handle.write(f"[ERROR] {message}\n")