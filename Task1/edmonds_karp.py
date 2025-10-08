from collections import deque, defaultdict
import networkx as nx
import matplotlib.pyplot as plt


# Функція для візуалізації графа
def visualize_graph(capacity, node_labels):
    G = nx.DiGraph()  # Створюємо спрямований граф
    n = len(capacity)

    # Додаємо вузли з мітками та шарами для multipartite_layout
    layers = {}
    layers[0] = 0  # Шар 0: Супер-джерело
    for i in [1, 2]:
        layers[i] = 1  # Шар 1: Термінали
    for i in [3, 4, 5, 6]:
        layers[i] = 2  # Шар 2: Склади
    for i in range(7, 21):
        layers[i] = 3  # Шар 3: Магазини
    layers[21] = 4  # Шар 4: Супер-стік

    for u in range(n):
        G.add_node(u, subset=layers[u], label=node_labels.get(u, str(u)))

    # Додаємо ребра з вагами
    for u in range(n):
        for v in range(n):
            if capacity[u][v] > 0:
                G.add_edge(u, v, weight=capacity[u][v])

    # Використовуємо multipartite_layout для шарового розміщення
    pos = nx.multipartite_layout(G, subset_key="subset", align="horizontal")

    # Малюємо граф
    plt.figure(figsize=(20, 10))
    nx.draw(
        G,
        pos,
        with_labels=True,
        labels={n: G.nodes[n]["label"] for n in G.nodes},
        node_color="lightblue",
        node_size=800,
        font_size=8,
        arrows=True,
        arrowstyle="->",
        arrowsize=15,
    )

    edge_labels = {}
    for u, v, data in G.edges(data=True):
        weight = data["weight"]
        if weight != inf:
            edge_labels[(u, v)] = weight

    nx.draw_networkx_edge_labels(
        G, pos, edge_labels=edge_labels, font_size=8, label_pos=0.5, rotate=True
    )

    plt.title("Візуалізація мережі потоків (шарова структура)")
    plt.show()


# Функція для пошуку збільшуючого шляху (BFS)
def bfs(capacity, flow_matrix, source, sink, parent):
    visited = [False] * len(capacity)
    queue = deque([source])
    visited[source] = True

    while queue:
        current_node = queue.popleft()

        for neighbor in range(len(capacity)):
            # Перевірка, чи є залишкова пропускна здатність у каналі
            if (
                not visited[neighbor]
                and capacity[current_node][neighbor]
                - flow_matrix[current_node][neighbor]
                > 0
            ):
                parent[neighbor] = current_node
                visited[neighbor] = True
                if neighbor == sink:
                    return True
                queue.append(neighbor)

    return False


# Основна функція для обчислення максимального потоку
def edmonds_karp(capacity, source, sink):
    num_nodes = len(capacity)
    flow_matrix = [
        [0] * num_nodes for _ in range(num_nodes)
    ]  # Ініціалізуємо матрицю потоку нулем
    parent = [-1] * num_nodes
    max_flow = 0
    step = 1
    terminal_flows = defaultdict(
        lambda: defaultdict(int)
    )  # Словник для відстеження потоків від терміналів до магазинів

    # Поки є збільшуючий шлях, додаємо потік
    while bfs(capacity, flow_matrix, source, sink, parent):
        # Знаходимо мінімальну пропускну здатність уздовж знайденого шляху (вузьке місце)
        path_flow = float("inf")
        current_node = sink

        while current_node != source:
            previous_node = parent[current_node]
            path_flow = min(
                path_flow,
                capacity[previous_node][current_node]
                - flow_matrix[previous_node][current_node],
            )
            current_node = previous_node

        # Реконструюємо шлях для відстеження терміналу та магазину
        path = []
        current = sink
        while current != source:
            path.append(current)
            current = parent[current]
        path.append(source)
        path.reverse()
        terminal = path[1]  # Термінал одразу після супер-джерела
        store = path[-2]  # Магазин перед супер-стоком
        terminal_flows[terminal][store] += path_flow

        # Виводимо крок
        print(f"Крок {step}: Збільшуючий шлях: {' -> '.join(map(str, path))}")
        print(f" Вузьке місце: {path_flow}")

        # Оновлюємо потік уздовж шляху, враховуючи зворотний потік
        current_node = sink
        while current_node != source:
            previous_node = parent[current_node]
            flow_matrix[previous_node][current_node] += path_flow
            flow_matrix[current_node][previous_node] -= path_flow
            current_node = previous_node

        # Збільшуємо максимальний потік
        max_flow += path_flow
        step += 1

    print(f"Максимальний потік: {max_flow}")

    # Виводимо таблицю потоків
    print("Таблиця потоків:")
    for terminal in [1, 2]:
        for store_node in range(7, 21):
            store_num = store_node - 6
            flow = terminal_flows[terminal].get(store_node, 0)
            print(f"Термінал {terminal}\tМагазин {store_num}\t{flow}")

    # Загальні потоки від терміналів
    total_t1 = sum(terminal_flows[1].values())
    total_t2 = sum(terminal_flows[2].values())
    print(f"Загальний з Терміналу 1: {total_t1}")
    print(f"Загальний з Терміналу 2: {total_t2}")

    return max_flow, terminal_flows


# Кількість вузлів: 0 - супер-джерело, 1-2 термінали, 3-6 склади, 7-20 магазини, 21 - супер-стік
num_nodes = 22
capacity = [[0 for _ in range(num_nodes)] for _ in range(num_nodes)]
inf = 9999  # "Нескінченність" для супер-джерела та стоку

# Додаємо ребра від супер-джерела до терміналів
capacity[0][1] = inf
capacity[0][2] = inf

# Ребра від терміналів до складів
capacity[1][3] = 25  # Термінал 1 -> Склад 1
capacity[1][4] = 20  # Термінал 1 -> Склад 2
capacity[1][5] = 15  # Термінал 1 -> Склад 3
capacity[2][4] = 10  # Термінал 2 -> Склад 2
capacity[2][5] = 15  # Термінал 2 -> Склад 3
capacity[2][6] = 30  # Термінал 2 -> Склад 4

# Ребра від складів до магазинів
capacity[3][7] = 15  # Склад 1 -> Магазин 1
capacity[3][8] = 10  # Склад 1 -> Магазин 2
capacity[3][9] = 20  # Склад 1 -> Магазин 3
capacity[4][10] = 15  # Склад 2 -> Магазин 4
capacity[4][11] = 10  # Склад 2 -> Магазин 5
capacity[4][12] = 25  # Склад 2 -> Магазин 6
capacity[5][13] = 20  # Склад 3 -> Магазин 7
capacity[5][14] = 15  # Склад 3 -> Магазин 8
capacity[5][15] = 10  # Склад 3 -> Магазин 9
capacity[6][16] = 20  # Склад 4 -> Магазин 10
capacity[6][17] = 10  # Склад 4 -> Магазин 11
capacity[6][18] = 15  # Склад 4 -> Магазин 12
capacity[6][19] = 5  # Склад 4 -> Магазин 13
capacity[6][20] = 10  # Склад 4 -> Магазин 14

# Ребра від магазинів до супер-стоку
for i in range(7, 21):
    capacity[i][21] = inf

# Мітки вузлів для візуалізації
node_labels = {
    0: "Супер-джерело",
    1: "Термінал 1",
    2: "Термінал 2",
    3: "Склад 1",
    4: "Склад 2",
    5: "Склад 3",
    6: "Склад 4",
    7: "Магазин 1",
    8: "Магазин 2",
    9: "Магазин 3",
    10: "Магазин 4",
    11: "Магазин 5",
    12: "Магазин 6",
    13: "Магазин 7",
    14: "Магазин 8",
    15: "Магазин 9",
    16: "Магазин 10",
    17: "Магазин 11",
    18: "Магазин 12",
    19: "Магазин 13",
    20: "Магазин 14",
    21: "Супер-стік",
}

# Візуалізуємо граф first
visualize_graph(capacity, node_labels)

# Джерело та стік
source = 0
sink = 21

# Запускаємо алгоритм (after graph visualization)
edmonds_karp(capacity, source, sink)
