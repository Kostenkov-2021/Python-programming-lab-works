# Программирование Python

# Лабораторная работа №2

## Костенков Данил Денисович

## Группа P4150





# Генератор бинарного дерева

Программа на Python для рекурсивного генерации бинарного дерева с различными структурами данных.

## Описание

Данная программа реализует рекурсивный алгоритм построения бинарного дерева с возможностью использования различных структур данных для хранения дерева:

- **Словарь** (dict) - основное представление
- **Список** (list) - компактное представление в виде кучи
- **NamedTuple** - типизованное представление с доступом через точки

## Требования

- Python 3.6+
- Стандартные библиотеки (collections, unittest)

## Установка

```bash
git clone <repository-url>
cd binary-tree-generator
```

## Использование

### Основная функция (словарь)

```python
from binary_tree import gen_bin_tree

# С параметрами по умолчанию (height=5, root=6)
tree = gen_bin_tree()

# С пользовательскими параметрами
tree = gen_bin_tree(height=3, root=10)
```

### Альтернативные представления

```python
from binary_tree import gen_bin_tree_list, gen_bin_tree_namedtuple

# Представление в виде списка
tree_list = gen_bin_tree_list(height=3, root=6)

# Представление через namedtuple
tree_named = gen_bin_tree_namedtuple(height=3, root=6)
```

## Алгоритм построения

Дерево строится по следующим правилам:

- **Корень**: задается пользователем (по умолчанию 6)
- **Высота**: задается пользователем (по умолчанию 5)
- **Левый потомок**: `(root * 2) - 2`
- **Правый потомок**: `root + 4`

### Пример для height=2, root=6:

```
      6
     / \
    10  10
```

### Пример для height=3, root=6:

```
        6
       / \
     10   10
    /  \  /  \
   18  14 18  14
```

## Функции

### `gen_bin_tree(height: int = 5, root: int = 6) -> Optional[dict]`

Рекурсивно генерирует бинарное дерево в виде словаря.

**Параметры:**
- `height` - высота дерева (≥1)
- `root` - значение корневого узла

**Возвращает:**
```python
{
    'root': value,
    'left': left_subtree,  # рекурсивно
    'right': right_subtree  # рекурсивно
}
```

### `gen_bin_tree_list(height: int = 5, root: int = 6) -> Optional[list]`

Рекурсивно генерирует бинарное дерево в виде списка.

**Возвращает:**
```python
[root, left_subtree, right_subtree]  # рекурсивно
```

### `gen_bin_tree_namedtuple(height: int = 5, root: int = 6) -> Optional[object]`

Рекурсивно генерирует бинарное дерево с использованием namedtuple.

**Возвращает:**
```python
Node(root=value, left=left_subtree, right=right_subtree)
```

## Примеры использования

### Базовый пример

```python
tree = gen_bin_tree(3, 6)
print(tree)
```

**Вывод:**
```python
{
    'root': 6,
    'left': {
        'root': 10,
        'left': {'root': 18, 'left': None, 'right': None},
        'right': {'root': 14, 'left': None, 'right': None}
    },
    'right': {
        'root': 10,
        'left': {'root': 18, 'left': None, 'right': None},
        'right': {'root': 14, 'left': None, 'right': None}
    }
}
```

### Сравнение представлений

```python
# Словарь
dict_tree = gen_bin_tree(2, 6)
# {'root': 6, 'left': {'root': 10, 'left': None, 'right': None}, 'right': {...}}

# Список  
list_tree = gen_bin_tree_list(2, 6)
# [6, [10, None, None], [10, None, None]]

# NamedTuple
named_tree = gen_bin_tree_namedtuple(2, 6)
# Node(root=6, left=Node(root=10, left=None, right=None), right=...)
```

## Тестирование

Для запуска тестов выполните:

```bash
python -m unittest binary_tree.py
```

или

```bash
python binary_tree.py
```

### Тестовые случаи

- Базовые случаи (высота 1, 2, 3)
- Параметры по умолчанию
- Некорректная высота
- Разные значения корня
- Согласованность между представлениями

```

## Особенности реализации

- **Рекурсивный подход** - естественное представление древовидных структур
- **Типизация** - использование аннотаций типов для лучшей читаемости
- **Граничные случаи** - корректная обработка высоты 0 и 1
- **Гибкость** - поддержка различных структур данных
- **Документация** - полное соответствие PEP-257

## Ограничения

- Максимальная высота ограничена максимальной глубиной рекурсии Python
- Для очень больших деревьев рекомендуется использовать итеративный подход
- Namedtuple создает новый тип для каждого вызова (можно оптимизировать)