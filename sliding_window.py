import random
from typing import Dict
import time
from collections import deque


class SlidingWindowRateLimiter:
    """A rate limiter using sliding window algorithm to control message frequency."""

    def __init__(self, window_size: int = 10, max_requests: int = 1):
        self.window_size = window_size
        self.max_requests = max_requests
        self.user_requests: Dict[
            str, deque
        ] = {}  # Словник для зберігання історії запитів

    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        if user_id not in self.user_requests:
            return

        window_start_time = current_time - self.window_size
        user_window = self.user_requests[user_id]

        while (
            user_window and user_window[0] <= window_start_time
        ):  # Видаляємо позначки старші за початок вікна
            user_window.popleft()

        if not user_window:
            del self.user_requests[user_id]

    def can_send_message(
        self, user_id: str
    ) -> bool:  # чи може користувач надіслати повідомлення
        current_time = time.time()
        self._cleanup_window(user_id, current_time)

        if (
            user_id not in self.user_requests
            or len(self.user_requests[user_id]) < self.max_requests
        ):
            return True  # Дозволено надіслати повідомлення

        return False

    def record_message(self, user_id: str) -> bool:
        if self.can_send_message(user_id):
            current_time = time.time()
            # Якщо користувача немає, створюємо нову чергу
            if user_id not in self.user_requests:
                self.user_requests[user_id] = deque()
            # Додаємо позначку часу для повідомлення
            self.user_requests[user_id].append(current_time)
            return True
        return False

    def time_until_next_allowed(self, user_id: str) -> float:
        current_time = time.time()
        self._cleanup_window(user_id, current_time)

        if (
            user_id not in self.user_requests
            or len(self.user_requests[user_id]) < self.max_requests
        ):
            return 0.0

        oldest_request_time = self.user_requests[user_id][0]
        time_to_wait = oldest_request_time + self.window_size - current_time

        return max(0.0, time_to_wait)


# Демонстрація роботи
def test_rate_limiter():
    """
    Тестова функція для демонстрації роботи Rate Limiter.
    """
    # Створюємо rate limiter: вікно 10 секунд, 1 повідомлення
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)

    # Симулюємо потік повідомлень від користувачів (послідовні ID від 1 до 20)
    print("\n=== Симуляція потоку повідомлень ===")
    for message_id in range(1, 11):
        # Симулюємо різних користувачів (ID від 1 до 5)
        user_id = str(message_id % 5 + 1)

        result = limiter.record_message(user_id)
        wait_time = limiter.time_until_next_allowed(user_id)

        print(
            f"Повідомлення {message_id:2d} | Користувач {user_id} | "
            f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}"
        )

        # Невелика затримка між повідомленнями для реалістичності
        # Випадкова затримка від 0.1 до 1 секунди
        time.sleep(random.uniform(0.1, 1.0))

    # Чекаємо, поки вікно очиститься
    print("\nОчікуємо 4 секунди...")
    time.sleep(4)

    print("\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        user_id = str(message_id % 5 + 1)
        result = limiter.record_message(user_id)
        wait_time = limiter.time_until_next_allowed(user_id)
        print(
            f"Повідомлення {message_id:2d} | Користувач {user_id} | "
            f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}"
        )
        # Випадкова затримка від 0.1 до 1 секунди
        time.sleep(random.uniform(0.1, 1.0))


if __name__ == "__main__":
    test_rate_limiter()
    print("\n=== Кінець програми ===")

"""
=== Симуляція потоку повідомлень ===
Повідомлення  1 | Користувач 2 | ✓
Повідомлення  2 | Користувач 3 | ✓
Повідомлення  3 | Користувач 4 | ✓
Повідомлення  4 | Користувач 5 | ✓
Повідомлення  5 | Користувач 1 | ✓
Повідомлення  6 | Користувач 2 | × (очікування 7.3с)
Повідомлення  7 | Користувач 3 | × (очікування 7.6с)
Повідомлення  8 | Користувач 4 | × (очікування 7.0с)
Повідомлення  9 | Користувач 5 | × (очікування 7.0с)
Повідомлення 10 | Користувач 1 | × (очікування 7.3с)

Очікуємо 4 секунди...

=== Нова серія повідомлень після очікування ===
Повідомлення 11 | Користувач 2 | × (очікування 0.4с)
Повідомлення 12 | Користувач 3 | × (очікування 0.9с)
Повідомлення 13 | Користувач 4 | × (очікування 0.7с)
Повідомлення 14 | Користувач 5 | × (очікування 0.5с)
Повідомлення 15 | Користувач 1 | × (очікування 0.4с)
Повідомлення 16 | Користувач 2 | ✓
Повідомлення 17 | Користувач 3 | ✓
Повідомлення 18 | Користувач 4 | ✓
Повідомлення 19 | Користувач 5 | ✓
Повідомлення 20 | Користувач 1 | ✓

=== Кінець програми ===
"""
