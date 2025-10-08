from trie import Trie  # Імпортуємо клас Trie з модуля trie


class Homework(Trie):
    # Функція для підрахунку кількості слів, що закінчуються заданим шаблоном
    def count_words_with_suffix(self, pattern) -> int:
        # Перевірка, що шаблон є рядком
        if not isinstance(pattern, str):
            raise TypeError("pattern must be a string")
        # Якщо шаблон порожній, повертаємо загальну кількість слів
        if not pattern:
            return self.size

        pattern_list = list(pattern)  # Перетворюємо шаблон у список символів
        plen = len(pattern)  # Зберігаємо довжину шаблону
        count = [0]  # Лічильник знайдених слів

        # Рекурсивна функція для обходу дерева
        def dfs(node, path):
            # Якщо вузол містить значення (слово)
            if node.value is not None:
                # Перевіряємо, чи закінчується слово на заданий шаблон
                if len(path) >= plen and path[-plen:] == pattern_list:
                    count[0] += 1  # Збільшуємо лічильник
            # Проходимо по всіх дочірніх вузлах
            for char, child in node.children.items():
                path.append(char)  # Додаємо символ до шляху
                dfs(child, path)  # Рекурсивний виклик для дочірнього вузла
                path.pop()  # Видаляємо символ з шляху

        dfs(self.root, [])  # Починаємо обхід з кореня
        return count[0]  # Повертаємо кількість знайдених слів

    # Функція для перевірки наявності слів із заданим префіксом
    def has_prefix(self, prefix) -> bool:
        if not isinstance(prefix, str):
            raise TypeError("prefix must be a string")
        # Якщо префікс порожній, перевіряємо, чи є хоча б одне слово
        if prefix == "":
            return self.size > 0

        current = self.root  # Розпочинаємо з кореня
        # Проходимо по символах префікса
        for char in prefix:
            # Якщо символ не знайдений, повертаємо False
            if char not in current.children:
                return False
            current = current.children[char]  # Переходимо до дочірнього вузла
        return True  # Якщо префікс знайдений, повертаємо True


if __name__ == "__main__":
    trie = Homework()  # Створюємо екземпляр Trie
    words = ["apple", "application", "banana", "cat"]  # Список слів
    for i, word in enumerate(words):
        trie.put(word, i)  # Додаємо слова до Trie

    # Перевірка кількості слів, що закінчуються на заданий суфікс
    assert trie.count_words_with_suffix("e") == 1  # apple
    assert trie.count_words_with_suffix("ion") == 1  # application
    assert trie.count_words_with_suffix("a") == 1  # banana
    assert trie.count_words_with_suffix("at") == 1  # cat

    # Перевірка наявності префікса
    assert trie.has_prefix("app") == True  # apple, application
    assert trie.has_prefix("bat") == False  # немає слів з префіксом "bat"
    assert trie.has_prefix("ban") == True  # banana
    assert trie.has_prefix("ca") == True  # cat

    print("Усі тести успішно пройдено.")  # Повідомлення про успішне проходження тестів
