import heapq
from math import sqrt


# Thuật toán A*
class AStarGraph:
    def __init__(self, graph):
        self.graph = graph

    def heuristic(self, a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])

        # Heuristics tám hướng
        return max(dx, dy) + (sqrt(2) - 1) * min(dx, dy)

    def find_path(self, start, end, restrict):
        pq = []
        heapq.heappush(pq, (0, start))
        came_from = {start: None}
        g_score = {start: 0}

        while pq:
            _, current = heapq.heappop(pq)

            if current in restrict:
                continue

            # Nếu thấy đích thì dừng
            if current == end:
                self.last_g_score = g_score[current]
                return self.reconstruct_path(came_from, end)

            for neighbor, cost in self.graph.get(current, []):
                new_cost = g_score[current] + cost

                if neighbor not in g_score or new_cost < g_score[neighbor]:
                    g_score[neighbor] = new_cost
                    priority = new_cost + self.heuristic(neighbor, end)
                    heapq.heappush(pq, (priority, neighbor))
                    came_from[neighbor] = current
        return None

    # Tìm đường đi từ đích ngược về đầu
    def reconstruct_path(self, came_from, end):
        path = []
        tmp = end

        while tmp is not None:
            path.append(tmp)
            tmp = came_from[tmp]
        return path[::-1]

    # Lấy g_score của đích
    def get_last_g_score(self):
        return self.last_g_score if hasattr(self, "last_g_score") else None
