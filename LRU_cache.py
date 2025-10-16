import random
import time
from collections import OrderedDict


class LRUCache:
    """LRU Cache implementation using OrderedDict."""

    def __init__(self, capacity):
        self.cache = OrderedDict()  # Ініціалізація кешу
        self.capacity = capacity

    def get(self, key):
        # Отримати значення за ключем; якщо ключа немає, повернути -1
        if key not in self.cache:
            return -1
        # Перемістити ключ до кінця (recently used)
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key, value):
        # Додати ключ-значення до кешу
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        # Якщо перевищено ємність, видалити LRU елемент
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)


# Without cache case
def range_sum_no_cache(array, left, right):
    return sum(array[left : right + 1])


def update_no_cache(array, index, value):
    array[index] = value


# With cache case
def range_sum_with_cache(array, left, right, cache):
    key = (left, right)
    result = cache.get(key)
    if result == -1:
        result = sum(array[left : right + 1])
        cache.put(key, result)
    return result


def update_with_cache(array, index, value, cache):
    # Оновити елемент масиву та інвалідувати кеш для діапазонів, що містять index
    array[index] = value
    # Знайти ключі, де left <= index <= right
    keys_to_remove = [key for key in cache.cache if key[0] <= index <= key[1]]
    # Видалити ці ключі з кешу
    for key in keys_to_remove:
        cache.cache.pop(key)


# Генератор запитів
def make_queries(n, q, hot_pool=30, p_hot=0.95, p_update=0.03):
    # Створити список із hot_pool "гарячих" діапазонів
    hot = [
        (random.randint(0, n // 2), random.randint(n // 2, n - 1))
        for _ in range(hot_pool)
    ]
    queries = []
    for _ in range(q):
        if random.random() < p_update:  # ~3% запитів — оновлення
            idx = random.randint(0, n - 1)
            val = random.randint(1, 100)
            queries.append(("Update", idx, val))
        else:  # ~97% — запити на суму
            if random.random() < p_hot:  # 95% — гарячі діапазони
                left, right = random.choice(hot)
            else:  # 5% — випадкові діапазони
                left = random.randint(0, n - 1)
                right = random.randint(left, n - 1)
            queries.append(("Range", left, right))
    return queries


def main():
    n = 100_000
    q = 50_000
    array = [random.randint(1, 100) for _ in range(n)]
    queries = make_queries(n, q)
    cache = LRUCache(1000)

    # Тестування без кешу
    array_no_cache = array.copy()
    start_time = time.perf_counter()
    for query in queries:
        if query[0] == "Range":
            _, left, right = query
            range_sum_no_cache(array_no_cache, left, right)
        else:  # Update
            _, index, value = query
            update_no_cache(array_no_cache, index, value)
    time_no_cache = time.perf_counter() - start_time  # Час без кешу

    # Тестування з кешем
    array_with_cache = array.copy()
    start_time = time.perf_counter()
    for query in queries:
        if query[0] == "Range":
            _, left, right = query
            range_sum_with_cache(array_with_cache, left, right, cache)
        else:  # Update
            _, index, value = query
            update_with_cache(array_with_cache, index, value, cache)
    time_with_cache = time.perf_counter() - start_time  # Час з кешем

    # Виведення результатів
    speedup = time_no_cache / time_with_cache if time_with_cache > 0 else float("inf")
    print(f"Без кешу : {time_no_cache:.2f} c")
    print(f"LRU-кеш  : {time_with_cache:.2f} c (прискорення ×{speedup:.1f})")


# Демонстрація роботи
if __name__ == "__main__":
    main()


# cd "/Users/macbook/Documents/GitHub/14 Data Structures_and_Algorithms/HW_Advanced/goit-algo2-hw-08"
# python3 LRU_cache.py
# Output: Без кешу : 38.17 c
# Output: LRU-кеш  : 15.41 c (прискорення ×2.5)
