def show_log_examples() -> None:
    """Показывает примеры логов из разных обработчиков."""
    
    print("\n" + "=" * 50)
    print("Примеры логов из разных обработчиков")
    print("=" * 50)
    
    # Пример 1: Логирование в StringIO
    print("\n1. Логирование в StringIO:")
    string_stream = io.StringIO()
    
    @logger(handle=string_stream)
    def multiply(x: int, y: int) -> int:
        return x * y
    
    try:
        result = multiply(5, 3)
        print(f"Результат: {result}")
    except:
        pass
    
    logs = string_stream.getvalue()
    print("Логи:")
    print(logs)
    
    # Пример 2: Логирование с ошибкой
    print("\n2. Логирование с ошибкой:")
    error_stream = io.StringIO()
    
    @logger(handle=error_stream)
    def divide(x: int, y: int) -> float:
        return x / y
    
    try:
        divide(10, 0)
    except ZeroDivisionError:
        print("Ошибка деления на ноль перехвачена")
    
    print("Логи с ошибкой:")
    print(error_stream.getvalue())
    
    # Пример 3: Логирование в файл
    print("\n3. Логирование в файл (создан файл 'example.log')")
    example_logger = logging.getLogger("example")
    example_logger.setLevel(logging.INFO)
    
    file_handler = logging.FileHandler("example.log", encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    example_logger.addHandler(file_handler)
    
    @logger(handle=example_logger)
    def add_numbers(a: int, b: int) -> int:
        return a + b
    
    add_numbers(7, 3)
    print("Логи записаны в файл 'example.log'")