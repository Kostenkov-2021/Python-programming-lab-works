# Программирование Python

# Лабораторная работа №7

## Костенков Данил Денисович

## Группа P4150


# Декоратор для логирования с параметрами

## Введение

Целью данной работы было создание параметризуемого декоратора для логирования с поддержкой различных обработчиков вывода. В процессе работы были освоены:

- Принципы разработки декораторов с параметрами
- Разделение ответственности функций (бизнес-логика) и декораторов (сквозная логика)
- Обработка исключений при работе с внешними API
- Логирование в разные типы потоков (sys.stdout, io.StringIO, logging)
- Тестирование функции и поведения логирования

## Реализация декоратора logger

### Основные характеристики

Декоратор `logger` реализован с следующими параметрами:

```python
def logger(func=None, *, handle=sys.stdout):
    ...
```

### Поддерживаемые обработчики

1. **Обычный поток вывода** (по умолчанию):
   ```python
   @logger
   def function(): ...
   ```

2. **Объект, реализующий интерфейс файла**:
   ```python
   stream = io.StringIO()
   @logger(handle=stream)
   def function(): ...
   ```

3. **Объект модуля logging**:
   ```python
   log = logging.getLogger("L1")
   @logger(handle=log)
   def function(): ...
   ```

### Функциональность декоратора

1. **Логирование вызовов функций**:
   - Уровень INFO: старт вызова с аргументами
   - Уровень INFO: успешное завершение с результатом

2. **Логирование исключений**:
   - Уровень ERROR: текст и тип исключения
   - Повторный выброс исключения

3. **Сохранение сигнатуры функций** с использованием `functools.wraps`

### Ключевые особенности реализации

- **Автоматическое определение типа обработчика**: декоратор проверяет, является ли `handle` экземпляром `logging.Logger`
- **Универсальность**: работает с любым объектом, имеющим методы `write()` или `info()`/`error()`
- **Безопасность**: не модифицирует поведение декорируемой функции, только добавляет логирование

## Функция get_currencies

### Назначение

Функция получает курсы валют от API ЦБ РФ и возвращает словарь с курсами для запрошенных валют.

### Сигнатура

```python
def get_currencies(
    currency_codes: List[str],
    url: str = "https://www.cbr-xml-daily.ru/daily_json.js",
    timeout: float = 10.0
) -> Dict[str, float]:
```

### Бизнес-логика

1. Выполняет HTTP-запрос к API ЦБ РФ
2. Извлекает словарь `Valute` из полученного JSON
3. Возвращает словарь вида `{"USD": 93.25, "EUR": 101.7}`

### Обработка ошибок

Функция выбрасывает следующие исключения:

| Ситуация | Исключение |
|----------|------------|
| API недоступен | `ConnectionError` |
| Некорректный JSON | `ValueError` |
| Нет ключа "Valute" | `KeyError` |
| Валюта отсутствует в данных | `KeyError` |
| Курс валюты имеет неверный тип | `TypeError` |

### Важное замечание

Функция **не содержит логирования** — только бизнес-логику. Все исключения пробрасываются для обработки декоратором.

## Интеграция с декоратором

### Базовое использование

```python
@logger(handle=sys.stdout)
def get_currencies_logged(currency_codes: List[str]) -> Dict[str, float]:
    return get_currencies(currency_codes)
```

### Файловое логирование

```python
# Настройка файлового логирования
file_logger = setup_file_logging("currencies.log")

@logger(handle=file_logger)
def get_currencies_file_logged(currency_codes: List[str]) -> Dict[str, float]:
    return get_currencies(currency_codes)
```

## Демонстрационный пример

### Функция solve_quadratic

Реализована функция для решения квадратного уравнения с демонстрацией различных сценариев логирования:

```python
@logger(handle=sys.stdout)
def solve_quadratic(a: float, b: float, c: float) -> Optional[Tuple[float, ...]]:
```

### Сценарии демонстрации

1. **INFO**: уравнение с двумя корнями
   ```python
   solve_quadratic(1, -5, 6)  # Корни: 2 и 3
   ```

2. **INFO**: уравнение с одним корнем
   ```python
   solve_quadratic(1, -4, 4)  # Корень: 2
   ```

3. **WARNING**: уравнение без действительных корней
   ```python
   solve_quadratic(1, 2, 5)  # Дискриминант < 0
   ```

4. **ERROR**: некорректные данные
   ```python
   solve_quadratic("abc", 2, 3)  # TypeError при преобразовании
   ```

5. **CRITICAL**: вырожденное уравнение
   ```python
   solve_quadratic(0, 0, 5)  # a=b=0
   ```

## Тестирование

### Структура тестов

1. **Тесты декоратора logger** (`TestLoggerDecorator`):
   - Логирование в stdout
   - Логирование в StringIO
   - Логирование ошибок
   - Логирование через logging.Logger

2. **Тесты функции get_currencies** (`TestGetCurrencies`):
   - Успешное получение курсов
   - Отсутствие валюты
   - Некорректный JSON
   - Отсутствие ключа "Valute"
   - Некорректный тип курса
   - Ошибка соединения

3. **Тесты логирования ошибок** (`TestStreamWrite`):
   - Проверка записи ERROR в поток
   - Проверка проброса исключений

4. **Тесты решения квадратного уравнения** (`TestSolveQuadratic`):
   - Два корня
   - Один корень
   - Нет действительных корней
   - Некорректные коэффициенты
   - Вырожденное уравнение

### Пример теста

```python
class TestStreamWrite(unittest.TestCase):
    def setUp(self):
        self.stream = io.StringIO()
        
        @logger(handle=self.stream)
        def wrapped():
            return get_currencies(['USD'], url="https://invalid")
        
        self.wrapped = wrapped
    
    def test_logging_error(self):
        with self.assertRaises(ConnectionError):
            self.wrapped()
        
        logs = self.stream.getvalue()
        self.assertIn("ERROR", logs)
        self.assertIn("ConnectionError", logs)
```

## Примеры логов

### 1. Успешное выполнение (stdout)

```
[INFO] Вызов функции solve_quadratic с аргументами: 1, -5, 6
[INFO] Функция solve_quadratic успешно завершилась. Результат: (3.0, 2.0)
```

### 2. Ошибка в функции (StringIO)

```
[INFO] Вызов функции divide с аргументами: 10, 0
[ERROR] Ошибка в функции divide: ZeroDivisionError - division by zero
```

### 3. Файловое логирование (logging)

```
2024-01-15 10:30:45,123 - currency_file - INFO - Вызов функции get_currencies_file_logged с аргументами: ['USD', 'EUR']
2024-01-15 10:30:45,456 - currency_file - INFO - Функция get_currencies_file_logged успешно завершилась. Результат: {'USD': 93.25, 'EUR': 101.7}
```

### 4. Логирование с исключением (logging)

```
2024-01-15 10:31:12,789 - currency_file - INFO - Вызов функции get_currencies_file_logged с аргументами: ['XYZ']
2024-01-15 10:31:12,790 - currency_file - ERROR - Ошибка в функции get_currencies_file_logged: KeyError - Валюта 'XYZ' отсутствует в данных API
Traceback (most recent call last):
  File "...", line ..., in wrapper
    result = f(*args, **kwargs)
  File "...", line ..., in get_currencies
    raise KeyError(f"Валюта '{code}' отсутствует в данных API")
KeyError: "Валюта 'XYZ' отсутствует в данных API"
```

# Как логировать ошибки внутри функции, если логирование вынесено в декоратор?


Когда логирование вынесено в декоратор, основной механизм логирования ошибок внутри функции строится на использовании исключений. Ключевые подходы к логированию :

#### 1. Исключения как основной механизм передачи ошибок

Функция должна выбрасывать исключения при возникновении ошибок. Декоратор перехватывает все исключения, логирует их с уровнем ERROR и пробрасывает дальше:

```python
def get_currencies(currency_codes):
    try:
        # бизнес-логика
    except requests.RequestException as e:
        raise ConnectionError(f"Ошибка подключения: {e}") from e
```

#### 2. Кастомные исключения с контекстом

Для более информативного логирования можно создавать специализированные исключения:

```python
class CurrencyAPIError(Exception):
    """Базовое исключение для ошибок API валют."""
    pass

class CurrencyNotFoundError(CurrencyAPIError):
    def __init__(self, currency_code):
        super().__init__(f"Валюта '{currency_code}' не найдена")
        self.currency_code = currency_code

# В функции
if currency_code not in data:
    raise CurrencyNotFoundError(currency_code)
```

#### 3. Разделение уровней детализации

Декоратор логирует только факт возникновения ошибки, но иногда внутри функции нужно зафиксировать дополнительные детали:

```python
def complex_operation(data):
    for item in data:
        try:
            process(item)
        except ProcessingError as e:
            # Можно добавить контекст
            e.add_context(f"Обрабатывался элемент: {item}")
            raise
```

#### 4. Колбэки для сложных операций

Если функция выполняет длительную операцию с множеством шагов, можно использовать колбэки:

```python
def process_batch(items, error_callback=None):
    for item in items:
        try:
            process(item)
        except Exception as e:
            if error_callback:
                error_callback(f"Ошибка обработки {item}: {e}")
            raise BatchProcessingError("Ошибка в пакетной обработке")
```

#### 5. Контекстные менеджеры

Для логирования этапов сложных операций:

```python
from contextlib import contextmanager

@contextmanager
def operation_step(name):
    """Контекстный менеджер для логирования шагов операции."""
    # Внутреннее состояние, не логируемое декоратором
    start_time = time.time()
    try:
        yield
    finally:
        duration = time.time() - start_time
        # Эта информация не попадет в логи декоратора
        # но может быть использована внутри функции
```

#### 6. Возврат результата с флагом ошибки

Альтернативный подход (не рекомендуется для Python):

```python
def operation_with_status():
    try:
        result = do_something()
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e), "type": type(e).__name__}
```

### Рекомендации

1. **Единообразие**: Все ошибки должны выбрасываться как исключения
2. **Информативность**: Исключения должны содержать достаточный контекст для отладки
3. **Соответствие уровням абстракции**: Исключения должны соответствовать уровню абстракции функции
4. **Цепочка исключений**: Используйте `raise ... from ...` для сохранения оригинальной трассировки

### Пример правильного подхода

```python
@logger(handle=sys.stdout)
def process_user_data(user_id: int) -> Dict:
    """Обработка данных пользователя."""
    
    # Внутренняя проверка без логирования
    if user_id <= 0:
        raise ValueError(f"Некорректный ID пользователя: {user_id}")
    
    try:
        data = fetch_from_api(user_id)
    except APIError as e:
        # Добавляем контекст и пробрасываем
        raise DataFetchError(f"Не удалось получить данные для пользователя {user_id}") from e
    
    # Дальнейшая обработка...
```

**Вывод**: При правильной архитектуре с использованием декораторов для логирования, функция фокусируется на бизнес-логике и выбрасывании исключений, а декоратор обеспечивает единообразное логирование всех вызовов. Это соответствует принципу единственной ответственности (Single Responsibility Principle) и упрощает поддержку кода.

## Заключение

В ходе работы успешно реализован параметризуемый декоратор для логирования, который поддерживает различные типы обработчиков вывода. Разработанная архитектура четко разделяет ответственность: функции содержат только бизнес-логику, а декоратор отвечает за сквозную функциональность логирования.

Реализация включает:
- Гибкий декоратор с поддержкой stdout, StringIO и logging.Logger
- Функцию работы с внешним API с корректной обработкой исключений
- Демонстрационные примеры с различными сценариями
- Полноценный набор тестов для всех компонентов
- Поддержку файлового логирования

Данная работа демонстрирует практическое применение декораторов в Python для реализации cross-cutting concerns и улучшения архитектуры приложений.

