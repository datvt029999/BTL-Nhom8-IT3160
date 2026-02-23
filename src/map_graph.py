from collections import defaultdict
from math import sqrt
from pandas import read_csv


class Map:
    def __init__(self, csv_path):
        self.road = 0
        self.none_road = 1

        # Chuyển dữ liệu từ tệp .csv thành ma trận dạng numpy
        self.matrix = read_csv(csv_path).to_numpy()

        # Chuyển ma trận thành đồ thị để tăng tốc độ tính toán
        self.graph = self.matrix_to_graph()

    def matrix_to_graph(self):
        # Map (Key: Tọa độ, Value: Danh sách (Tọa độ, Chi phí))
        graph = defaultdict(list)

        # Loang tám hướng
        directions = [
            (1, 1),
            (1, 0),
            (1, -1),
            (0, -1),
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, 1),
        ]

        # Số hàng và số cột
        rows, columns = self.matrix.shape

        # Thuật toán tìm kiếm theo chiều sâu (Breadth first search - BFS)
        for x in range(rows):
            for y in range(columns):
                if self.matrix[x, y] == self.road:
                    for dx, dy in directions:
                        nx = x + dx
                        ny = y + dy

                        if (
                            0 <= nx <= rows
                            and 0 <= ny <= columns
                            and self.matrix[nx, ny] == 0
                        ):
                            # Chi phí của ngang hoặc dọc là 1
                            if dx == 0 or dy == 0:
                                cost = 1

                            # Chi phí của chéo là căn 2
                            else:
                                cost = sqrt(2)

                            graph[(x, y)].append(((nx, ny), cost))

        return graph

    def euclidean_distance(self, a, b):
        return sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    # Tìm node gần nhất là đường trong đồ thị
    def nearest_node(self, r, c):
        min_d = float("inf")
        dest = (0, 0)
        curr = (r, c)

        for k in self.graph.keys():
            if k == curr:
                continue
            dist = self.euclidean_distance(k, curr)

            if dist < min_d:
                min_d = dist
                dest = k
        return dest
